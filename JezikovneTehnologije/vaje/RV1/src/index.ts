import * as fs from 'fs';
import * as path from 'path';
import { XMLParser } from 'fast-xml-parser';

interface Patterns {
  front: { startMarkers: string[]; endMarkers: string[] };
  body: { startMarkers: string[]; endMarkers: string[] };
  back: { startMarkers: string[] };
  toc: { markers: string[] };
  toa: { markers: string[] };
  abstractSlo: { markers: string[] };
  abstractEn: { markers: string[] };
  chapter: { pattern: string };
  conclusion: { markers: string[] };
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

class TextSegmenter {
  private patterns: Patterns;

  constructor() {
    const patternsPath = path.join(__dirname, 'config', 'patterns.json');
    this.patterns = JSON.parse(fs.readFileSync(patternsPath, 'utf8'));
  }

  private matchesAnyPattern(text: string, patterns: string[]): boolean {
    return patterns.some(pattern => new RegExp(pattern, 'i').test(text));
  }

  private classifyPage(page: Page): string {
    // Check if page contains any markers for different sections
    const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
    const pageText = paragraphs.map(p => p['#text']).join(' ');

    // Check for end markers first to avoid misclassification
    if (this.matchesAnyPattern(pageText, this.patterns.front.endMarkers)) {
      return 'body';
    }
    if (this.matchesAnyPattern(pageText, this.patterns.body.endMarkers)) {
      return 'back';
    }

    // Then check for section start markers
    if (this.matchesAnyPattern(pageText, this.patterns.front.startMarkers)) {
      return 'front';
    }

    // Check for back matter first (since it might contain some body markers)
    if (this.matchesAnyPattern(pageText, this.patterns.back.startMarkers)) {
      return 'back';
    }

    // Check for body
    if (this.matchesAnyPattern(pageText, this.patterns.body.startMarkers)) {
      return 'body';
    }
    
    return 'unknown';
  }

  private classifyParagraph(text: string, lang: string): string {

    if (this.matchesAnyPattern(text, this.patterns.toc.markers)) {
      return 'toc';
    }
    if (this.matchesAnyPattern(text, this.patterns.toa.markers)) {
      return 'toa';
    }
    if (this.matchesAnyPattern(text, this.patterns.abstractSlo.markers)) {
      return 'abstractSlo';
    }
    if (this.matchesAnyPattern(text, this.patterns.abstractEn.markers)) {
      return 'abstractEn';
    }
    if (new RegExp(this.patterns.chapter.pattern).test(text)) {
      return 'chapter';
    }
    if (this.matchesAnyPattern(text, this.patterns.conclusion.markers)) {
      return 'conclusion';
    }
    
    return '';
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
    
    const output: string[] = [];
    output.push('ID CLASS');
    
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const pageClass = this.classifyPage(page);
      
      const paragraphs = Array.isArray(page.p) ? page.p : [page.p];
      for (let j = 0; j < paragraphs.length; j++) {
        const paragraph = paragraphs[j];
        const paraClass = this.classifyParagraph(paragraph['#text'], paragraph['@_xml:lang']);
        if (paraClass) {
          output.push(`${paragraph['@_xml:id']} ${paraClass}`);
        }
      }
      
      // Add page classification at the end
      output.push(`${page['@_xml:id']} ${pageClass}`);
    }
    
    // Create output directory if it doesn't exist
    const outputDir = path.join(__dirname, '..', 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir);
    }
    
    // Get just the filename without path and extension
    const baseName = path.basename(xmlPath).replace('.text.xml', '');
    const resPath = path.join(outputDir, `${baseName}.res`);
    
    fs.writeFileSync(resPath, output.join('\n'));
    console.log(`Results written to: ${resPath}`);
  }
}

// Usage
const segmenter = new TextSegmenter();
const files = [
  'kas-4000.text.xml'
];

files.forEach(file => {
  const xmlPath = path.join(__dirname, '..', 'korpus', file);
  const startTime = performance.now();
  segmenter.processXMLFile(xmlPath);
  const endTime = performance.now();
  const processingTime = endTime - startTime;
  console.log(`Processed ${file} in ${processingTime.toFixed(2)}ms`);
}); 