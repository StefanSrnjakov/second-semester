"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const fast_xml_parser_1 = require("fast-xml-parser");
class TextSegmenter {
    constructor() {
        this.currentSection = 'unknown';
        const patternsPath = path.join(__dirname, 'config', 'patterns.json');
        this.patterns = JSON.parse(fs.readFileSync(patternsPath, 'utf8'));
    }
    matchesAnyPattern(text, patterns) {
        return patterns.some(pattern => new RegExp(pattern, 'i').test(text));
    }
    classifyParagraph(text, lang) {
        const { lineMarkers } = this.patterns;
        // Check for TOC - special case with content markers
        if (this.matchesAnyPattern(text, lineMarkers.toc.startMarkers) ||
            (lineMarkers.toc.contentMarkers && this.matchesAnyPattern(text, lineMarkers.toc.contentMarkers))) {
            return { class: 'toc' };
        }
        // Check other line markers
        if (this.matchesAnyPattern(text, lineMarkers.toa.startMarkers)) {
            return { class: 'toa' };
        }
        if (this.matchesAnyPattern(text, lineMarkers.abstractSlo.startMarkers)) {
            return { class: 'abstractSlo' };
        }
        if (this.matchesAnyPattern(text, lineMarkers.abstractEn.startMarkers)) {
            return { class: 'abstractEn' };
        }
        if (this.matchesAnyPattern(text, lineMarkers.conclusion.startMarkers)) {
            return { class: 'conclusion' };
        }
        if (this.matchesAnyPattern(text, lineMarkers.chapter.startMarkers)) {
            return {
                class: 'chapter',
                title: text.trim()
            };
        }
        return { class: '' };
    }
    findSectionBoundaries(pages) {
        let frontToBody = -1;
        let bodyToBack = -1;
        // First pass: find the start of body (UVOD/Introduction)
        for (let i = 0; i < pages.length; i++) {
            const page = pages[i];
            const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
            // Check each paragraph for body start markers
            for (const para of paragraphs) {
                // Skip if paragraph or text is undefined
                if (!para || !para['#text'])
                    continue;
                const text = para['#text'];
                if (this.matchesAnyPattern(text, this.patterns.pageMarkers.body.startMarkers)) {
                    frontToBody = i;
                    break;
                }
            }
            if (frontToBody !== -1)
                break;
        }
        // Second pass: find the start of back matter
        if (frontToBody !== -1) {
            for (let i = frontToBody + 1; i < pages.length; i++) {
                const page = pages[i];
                const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
                for (const para of paragraphs) {
                    // Skip if paragraph or text is undefined
                    if (!para || !para['#text'])
                        continue;
                    const text = para['#text'];
                    if (this.matchesAnyPattern(text, this.patterns.pageMarkers.back.startMarkers)) {
                        bodyToBack = i;
                        break;
                    }
                }
                if (bodyToBack !== -1)
                    break;
            }
        }
        // If we didn't find the transitions, make some assumptions
        if (frontToBody === -1)
            frontToBody = 4; // Assume first 4 pages are front matter
        if (bodyToBack === -1)
            bodyToBack = pages.length - 2; // Assume last 2 pages are back matter
        console.log(`Found boundaries: front->body at page ${frontToBody}, body->back at page ${bodyToBack}`);
        return { frontToBody, bodyToBack };
    }
    processXMLFile(xmlPath) {
        const xmlContent = fs.readFileSync(xmlPath, 'utf8');
        const parser = new fast_xml_parser_1.XMLParser({
            ignoreAttributes: false,
            attributeNamePrefix: "@_",
            textNodeName: "#text"
        });
        const result = parser.parse(xmlContent);
        const pages = Array.isArray(result.document.page) ?
            result.document.page :
            [result.document.page];
        // Find section boundaries first
        const { frontToBody, bodyToBack } = this.findSectionBoundaries(pages);
        const output = [];
        output.push('ID,CLASS,TITLE');
        // Process all paragraphs for line markers
        for (const page of pages) {
            const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
            for (const paragraph of paragraphs) {
                // Skip if paragraph or text is undefined
                if (!paragraph || !paragraph['#text'])
                    continue;
                const classification = this.classifyParagraph(paragraph['#text'], paragraph['@_xml:lang']);
                if (classification.class) {
                    const title = classification.class === 'chapter' ? `,"${classification.title}"` : ',';
                    output.push(`${paragraph['@_xml:id']},${classification.class}${title}`);
                }
            }
        }
        // Classify pages based on their position relative to the boundaries
        pages.forEach((page, index) => {
            let pageClass = 'unknown';
            if (index < frontToBody) {
                pageClass = 'front';
            }
            else if (index >= frontToBody && index < bodyToBack) {
                pageClass = 'body';
            }
            else {
                pageClass = 'back';
            }
            output.push(`${page['@_xml:id']},${pageClass},`);
        });
        const outputDir = path.join(__dirname, '..', 'output');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir);
        }
        const baseName = path.basename(xmlPath).replace('.text.xml', '');
        const resPath = path.join(outputDir, `${baseName}.res`);
        fs.writeFileSync(resPath, output.join('\n'));
        console.log(`Results written to: ${resPath}`);
    }
}
// Usage
const segmenter = new TextSegmenter();
const files = [
    'kas-4000.text.xml',
    'kas-5000.text.xml',
    'kas-6000.text.xml',
    'kas-7000.text.xml',
    'kas-8000.text.xml',
    'kas-9000.text.xml'
];
files.forEach(file => {
    const xmlPath = path.join(__dirname, '..', 'korpus', file);
    const startTime = performance.now();
    segmenter.processXMLFile(xmlPath);
    const endTime = performance.now();
    const processingTime = endTime - startTime;
    console.log(`Processed ${file} in ${processingTime.toFixed(2)}ms`);
});
