
export interface SearchResult {
  x: number;
  y: number;
  z: number;
  timeToFindChunk: number;
  timeToFindPoint: number;
  totalTime: number;
}

interface TreeNode {
  start?: number;
  stop?: number;
  split?: number;
  delim?: number;
  dimension?: 'x' | 'y';
  left?: string;
  right?: string;
  leaf?: boolean;
}

interface TreeData {
  root: string;
  nodes: { [key: string]: TreeNode };
}

export const searchCoordinates = async (
  xValue: string, 
  yValue: string, 
  config: { treeData: string; pointsData: string }
): Promise<SearchResult> => {
  // wait for 3 seconds
  await new Promise(resolve => setTimeout(resolve, 500));
  const startTime = performance.now();
  const x = parseFloat(xValue);
  const y = parseFloat(yValue);
  
  // Load tree data
  const treeData: TreeData = await fetch(config.treeData).then(res => res.json());
  
  // Traverse tree to find leaf node
  let currentNode = treeData.nodes[treeData.root];
  
  while (!currentNode.leaf) {
    const value = currentNode.dimension === 'x' ? x : y;
    const nextNodeId = value < currentNode.delim! ? currentNode.left! : currentNode.right!;
    currentNode = treeData.nodes[nextNodeId];
  }

  // Calculate range in binary file
  const startByte = currentNode.start! * 12; // 3 floats * 4 bytes each
  const length = (currentNode.stop! - currentNode.start!) * 12;

  const timeToFindChunk = performance.now() - startTime;
  const timeStart2 = performance.now();
  // Load relevant section of binary file
  const response = await fetch(config.pointsData, {
    headers: {
      'Range': `bytes=${startByte}-${startByte + length - 1}`
    }
  });
  
  const buffer = await response.arrayBuffer();
  const points = new Float32Array(buffer);
  
  // Search for closest point in the loaded section
  let minDistance = Infinity;
  let closestPoint : { x: number, y: number, z: number } | null = null;
  for (let i = 0; i < points.length; i += 3) {
    const px = points[i];
    const py = points[i + 1];
    const pz = points[i + 2];
    
    const distance = Math.sqrt(
      Math.pow(x - px, 2) + 
      Math.pow(y - py, 2)
    );
    
    if (distance < minDistance) {
      minDistance = distance;
      closestPoint = { x: px, y: py, z: pz };
    }
  }

  const timePerformance = performance.now() - timeStart2;
  
  return { 
    x:closestPoint?.x || 0, 
    y:closestPoint?.y || 0, 
    z:closestPoint?.z || 0, 
    timeToFindChunk: timeToFindChunk,
    timeToFindPoint: timePerformance,
    totalTime: timePerformance + timeToFindChunk
  };
}; 