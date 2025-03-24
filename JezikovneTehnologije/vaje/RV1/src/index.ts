import * as fs from 'fs';
import * as path from 'path';
import { XMLParser } from 'fast-xml-parser';

interface MarkerSet {
  startMarkers: string[];
  endMarkers?: string[];
  contentMarkers?: string[];
}

interface Patterns {
  pageMarkers: {
    front: MarkerSet;
    body: MarkerSet;
    back: MarkerSet;
  };
  lineMarkers: {
    toc: MarkerSet;
    toa: { startMarkers: string[] };
    abstractSlo: { startMarkers: string[] };
    abstractEn: { startMarkers: string[] };
    chapter: { startMarkers: string[] };
    conclusion: { startMarkers: string[] };
  };
}

interface Page {
  '@_xml:id': string;
  '@_n': string;
  p: Array<{
    '@_xml:id': string;
    '@_xml:lang': string;
    '#text': string;
  }>;
}

interface ClassificationResult {
  class: string;
  title?: string;
}

class TextSegmenter {
  private patterns: Patterns;
  private currentSection: string = 'unknown';

  constructor() {
    const patternsPath = path.join(__dirname, 'config', 'patterns.json');
    this.patterns = JSON.parse(fs.readFileSync(patternsPath, 'utf8'));
  }

  private matchesAnyPattern(text: string, patterns: string[]): boolean {
    return patterns.some(pattern => new RegExp(pattern, 'i').test(text));
  }

  private classifyParagraph(text: string, lang: string): ClassificationResult {
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

  private findSectionBoundaries(pages: Page[]): { frontToBody: number; bodyToBack: number } {
    let frontToBody = -1;
    let bodyToBack = -1;

    // First pass: find the start of body (UVOD/Introduction)
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
      
      // Check each paragraph for body start markers
      for (const para of paragraphs) {
        // Skip if paragraph or text is undefined
        if (!para || !para['#text']) continue;
        
        const text = para['#text'];
        if (this.matchesAnyPattern(text, this.patterns.pageMarkers.body.startMarkers)) {
          frontToBody = i;
          break;
        }
      }
      if (frontToBody !== -1) break;
    }

    // Second pass: find the start of back matter
    if (frontToBody !== -1) {
      for (let i = frontToBody + 1; i < pages.length; i++) {
        const page = pages[i];
        const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
        
        for (const para of paragraphs) {
          // Skip if paragraph or text is undefined
          if (!para || !para['#text']) continue;
          
          const text = para['#text'];
          if (this.matchesAnyPattern(text, this.patterns.pageMarkers.back.startMarkers)) {
            bodyToBack = i;
            break;
          }
        }
        if (bodyToBack !== -1) break;
      }
    }

    // If we didn't find the transitions, make some assumptions
    if (frontToBody === -1) frontToBody = 4; // Assume first 4 pages are front matter
    if (bodyToBack === -1) bodyToBack = pages.length - 2; // Assume last 2 pages are back matter

    console.log(`Found boundaries: front->body at page ${frontToBody}, body->back at page ${bodyToBack}`);
    return { frontToBody, bodyToBack };
  }

  public processXMLFile(xmlPath: string): void {
    const xmlContent = fs.readFileSync(xmlPath, 'utf8');
    const parser = new XMLParser({
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
    
    const output: string[] = [];
    output.push('ID,CLASS,TITLE');
    
    // Process all paragraphs for line markers
    for (const page of pages) {
      const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
      for (const paragraph of paragraphs) {
        // Skip if paragraph or text is undefined
        if (!paragraph || !paragraph['#text']) continue;
        
        const classification = this.classifyParagraph(paragraph['#text'], paragraph['@_xml:lang']);
        if (classification.class) {
          const title = classification.class === 'chapter' ? `,"${classification.title}"` : ',';
          output.push(`${paragraph['@_xml:id']},${classification.class}${title}`);
        }
      }
    }
    
    // Classify pages based on their position relative to the boundaries
    pages.forEach((page : Page, index : number) => {
      let pageClass = 'unknown';
      if (index < frontToBody) {
        pageClass = 'front';
      } else if (index >= frontToBody && index < bodyToBack) {
        pageClass = 'body';
      } else {
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