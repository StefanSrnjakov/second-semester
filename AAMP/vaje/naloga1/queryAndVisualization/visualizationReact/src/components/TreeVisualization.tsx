import { useEffect, useState } from 'react';
import Tree from 'react-d3-tree';
import { Box, CircularProgress, Modal, IconButton } from '@mui/material';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import CloseIcon from '@mui/icons-material/Close';

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

interface CustomNodeProps {
  nodeDatum: any;
  isHighlighted: boolean;
}

interface TreeVisualizationProps {
  x: string;
  y: string;
  config: {
    treeData: string;
    pointsData: string;
  };
  onTreeLoad: (data: any) => void;
}

const CustomNode = ({ nodeDatum, isHighlighted }: CustomNodeProps) => (
  <g>
    <circle 
      r={120}
      fill={isHighlighted ? '#2196f3' : '#4caf50'}
    />
    <text
      dy="-1em"
      x="0"
      textAnchor="middle"
      style={{ fontSize: '30px', fill: '#000' }}
    >
      {nodeDatum.dimension?.toUpperCase() || 'LEAF'}
    </text>
    <text
      dy="0.3em"
      x="0"
      textAnchor="middle"
      style={{ fontSize: '30px', fill: '#000' }}
    >
      {nodeDatum.delim?.toFixed(2) || `${nodeDatum.start}-${nodeDatum.stop}`}
    </text>
    {!nodeDatum.dimension && (
      <text
        dy="1.8em"
        x="0"
        textAnchor="middle"
        style={{ fontSize: '30px', fill: '#000' }}
      >
        {`${nodeDatum.stop - nodeDatum.start} points`}
      </text>
    )}
  </g>
);

const TreeVisualization = ({ x, y, config, onTreeLoad }: TreeVisualizationProps) => {
  const [treeData, setTreeData] = useState<any>(null);
  const [highlightedPath, setHighlightedPath] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const transformTreeData = (treeJson: TreeData) => {
    const convertNode = (nodeId: string): any => {
      const node = treeJson.nodes[nodeId];
      if (node.leaf) {
        return {
          name: nodeId,
          attributes: {
            leaf: true,
            start: node.start,
            stop: node.stop
          }
        };
      }

      return {
        name: nodeId,
        attributes: {
          dimension: node.dimension,
          delim: node.delim
        },
        children: [
          convertNode(node.left!),
          convertNode(node.right!)
        ]
      };
    };

    return convertNode(treeJson.root);
  };

  const calculatePath = (treeJson: TreeData, xVal: number, yVal: number) => {
    const path: string[] = [];
    let currentNode = treeJson.nodes[treeJson.root];
    let currentId = treeJson.root;

    while (!currentNode.leaf) {
      path.push(currentId);
      const value = currentNode.dimension === 'x' ? xVal : yVal;
      currentId = value < currentNode.delim! ? currentNode.left! : currentNode.right!;
      currentNode = treeJson.nodes[currentId];
    }
    path.push(currentId);
    return path;
  };

  useEffect(() => {
    const loadTree = async () => {
      try {
        const response = await fetch(config.treeData);
        const treeJson: TreeData = await response.json();
        const transformed = transformTreeData(treeJson);
        setTreeData(transformed);
        onTreeLoad(transformed);

        if (x && y) {
          const path = calculatePath(treeJson, parseFloat(x), parseFloat(y));
          setHighlightedPath(path);
        }
      } catch (error) {
        console.error('Failed to load tree:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTree();
  }, [x, y, config.treeData, onTreeLoad]);

  const renderTree = (fullScreen: boolean) => (
    <Tree
      data={treeData}
      orientation="vertical"
      pathFunc="step"
      nodeSize={{ x: 150, y: 300 }}
      renderCustomNodeElement={(nodeInfo) => 
        CustomNode({ 
          nodeDatum: nodeInfo.nodeDatum.attributes,
          isHighlighted: highlightedPath.includes(nodeInfo.nodeDatum.name)
        })
      }
      separation={{ siblings: 2, nonSiblings: 2.5 }}
      translate={{ 
        x: fullScreen ? window.innerWidth / 2 : 400,
        y: fullScreen ? 200 : 150 
      }}
      zoom={fullScreen ? 0.3 : 0.5}
      scaleExtent={{ min: 0.1, max: 1.5 }}
      pathClassFunc={(edge) => {
        
        const isHighlighted = highlightedPath.includes(edge.source.data.name) && 
                             highlightedPath.includes(edge.target.data.name);
        
        return isHighlighted ? 'path-highlighted' : 'path-normal';
      }}
    />
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Box sx={{ 
        width: '100%', 
        height: '600px',
        position: 'relative',
        bgcolor: '#f5f5f5',
        borderRadius: 2,
        boxShadow: 1,
        '& .path-highlighted.rd3t-link': {
          stroke: '#2196f3 !important',
          strokeWidth: '12px !important',
        },
        '& .path-normal.rd3t-link': {
          stroke: '#90a4ae !important',
          strokeWidth: '2px !important',
        }
      }}>
        {treeData && (
          <>
            {renderTree(false)}
            <IconButton
              onClick={() => setIsModalOpen(true)}
              sx={{
                position: 'absolute',
                top: 10,
                right: 10,
                bgcolor: 'background.paper',
                '&:hover': {
                  bgcolor: 'background.paper',
                }
              }}
            >
              <FullscreenIcon />
            </IconButton>
          </>
        )}
      </Box>

      <Modal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        sx={{
          bgcolor: 'background.paper',
          '& .path-highlighted.rd3t-link': {
            stroke: '#2196f3 !important',
            strokeWidth: '12px !important',
          },
          '& .path-normal.rd3t-link': {
            stroke: '#90a4ae !important',
            strokeWidth: '2px !important',
          }
        }}
      >
        <Box sx={{ 
          width: '100vw', 
          height: '100vh',
          position: 'relative',
          bgcolor: '#f5f5f5'
        }}>
          {treeData && renderTree(true)}
          <IconButton
            onClick={() => setIsModalOpen(false)}
            sx={{
              position: 'absolute',
              top: 20,
              right: 20,
              bgcolor: 'background.paper',
              '&:hover': {
                bgcolor: 'background.paper',
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </Modal>
    </>
  );
};

export default TreeVisualization; 