import { useEffect, useRef } from 'react';
import { Box } from '@mui/material';

interface CoordinateVisualizationProps {
  treeData: any;
  width?: number;
  height?: number;
  highlightedPoint?: { x: number; y: number };
  onCoordinateClick?: (x: number, y: number) => void;
}

const CoordinateVisualization = ({ treeData, width = 400, height = 400, highlightedPoint, onCoordinateClick }: CoordinateVisualizationProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const padding = 40;
  const effectiveWidth = width - 2 * padding;
  const effectiveHeight = height - 2 * padding;

  // Calculate bounds from tree data
  const calculateBounds = (node: any) => {
    if (!node) return null;

    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;

    const updateBounds = (node: any) => {
      // Update bounds for split points
      if (node.attributes?.dimension === 'x') {
        minX = Math.min(minX, node.attributes.delim);
        maxX = Math.max(maxX, node.attributes.delim);
      } else if (node.attributes?.dimension === 'y') {
        minY = Math.min(minY, node.attributes.delim);
        maxY = Math.max(maxY, node.attributes.delim);
      }

      // Check leaf node points
      if (node.attributes?.points) {
        node.attributes.points.forEach((point: any) => {
          minX = Math.min(minX, point.x);
          maxX = Math.max(maxX, point.x);
          minY = Math.min(minY, point.y);
          maxY = Math.max(maxY, point.y);
        });
      }

      // Also check start/stop bounds if available
      if (node.attributes?.start !== undefined) {
        const { start, stop } = node.attributes;
        if (start.x !== undefined) {
          minX = Math.min(minX, start.x, stop.x);
          maxX = Math.max(maxX, start.x, stop.x);
        }
        if (start.y !== undefined) {
          minY = Math.min(minY, start.y, stop.y);
          maxY = Math.max(maxY, start.y, stop.y);
        }
      }

      if (node.children) {
        node.children.forEach(updateBounds);
      }
    };

    updateBounds(node);

    // If no bounds were found, use reasonable defaults
    if (minX === Infinity) {
      minX = -100;
      maxX = 100;
      minY = -100;
      maxY = 100;
    }

    // Add some padding to the bounds (10%)
    const xRange = maxX - minX || 1;
    const yRange = maxY - minY || 1;
    const xPadding = xRange * 0.1;
    const yPadding = yRange * 0.1;

    return {
      minX: minX - xPadding,
      maxX: maxX + xPadding,
      minY: minY - yPadding,
      maxY: maxY + yPadding
    };
  };

  const drawSplitLines = (
    ctx: CanvasRenderingContext2D, 
    node: any, 
    bounds: any,
    parentBounds: {
      minX: number,
      maxX: number,
      minY: number,
      maxY: number
    } = {
      minX: bounds.minX,
      maxX: bounds.maxX,
      minY: bounds.minY,
      maxY: bounds.maxY
    },
    level: number = 0
  ) => {
    if (!node.attributes?.dimension) return;

    const { dimension, delim } = node.attributes;
    const isXSplit = dimension === 'x';

    // Scale the delimiter and parent bounds to canvas coordinates
    const scaledDelim = isXSplit 
      ? padding + ((delim - bounds.minX) / (bounds.maxX - bounds.minX)) * effectiveWidth
      : padding + effectiveHeight - ((delim - bounds.minY) / (bounds.maxY - bounds.minY)) * effectiveHeight;

    // Scale parent bounds to canvas coordinates
    const scaledBounds = {
      top: padding + effectiveHeight - ((parentBounds.maxY - bounds.minY) / (bounds.maxY - bounds.minY)) * effectiveHeight,
      bottom: padding + effectiveHeight - ((parentBounds.minY - bounds.minY) / (bounds.maxY - bounds.minY)) * effectiveHeight,
      left: padding + ((parentBounds.minX - bounds.minX) / (bounds.maxX - bounds.minX)) * effectiveWidth,
      right: padding + ((parentBounds.maxX - bounds.minX) / (bounds.maxX - bounds.minX)) * effectiveWidth
    };

    ctx.beginPath();
    ctx.strokeStyle = isXSplit 
      ? `rgba(255,0,0,${Math.max(0.4, 0.9 - level * 0.1)})`
      : `rgba(0,0,255,${Math.max(0.4, 0.9 - level * 0.1)})`;
    ctx.lineWidth = Math.max(2, 6 - level);
    
    if (isXSplit) {
      ctx.moveTo(scaledDelim, scaledBounds.top);
      ctx.lineTo(scaledDelim, scaledBounds.bottom);
    } else {
      ctx.moveTo(scaledBounds.left, scaledDelim);
      ctx.lineTo(scaledBounds.right, scaledDelim);
    }
    ctx.stroke();

    if (node.children) {
      // Calculate new bounds for children based on the split
      const leftBounds = { ...parentBounds };
      const rightBounds = { ...parentBounds };

      if (isXSplit) {
        leftBounds.maxX = delim;
        rightBounds.minX = delim;
      } else {
        leftBounds.maxY = delim;
        rightBounds.minY = delim;
      }

      if (node.children[0]) {
        drawSplitLines(ctx, node.children[0], bounds, leftBounds, level + 1);
      }
      if (node.children[1]) {
        drawSplitLines(ctx, node.children[1], bounds, rightBounds, level + 1);
      }
    }
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    // wait for 3 seconds
    if (!canvasRef.current || !onCoordinateClick) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Convert click coordinates back to data space
    const bounds = calculateBounds(treeData) || {
      minX: -100, maxX: 100,  // More reasonable default bounds
      minY: -100, maxY: 100
    };

    const dataX = Math.round(
      ((x - padding) / effectiveWidth) * (bounds.maxX - bounds.minX) + bounds.minX
    );
    const dataY = Math.round(
      bounds.maxY - ((y - padding) / effectiveHeight) * (bounds.maxY - bounds.minY)
    );

    onCoordinateClick(dataX, dataY);
  };

  useEffect(() => {
    if (!canvasRef.current || !treeData) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, width, height);

    // Calculate bounds from tree data
    const bounds = calculateBounds(treeData) || {
      minX: -100, maxX: 100,  // More reasonable default bounds
      minY: -100, maxY: 100
    };


    // Draw grid and numbers
    ctx.strokeStyle = '#eee';
    ctx.lineWidth = 1;
    
    // Calculate step size for labels (5 steps)
    const xStep = Math.ceil((bounds.maxX - bounds.minX) / 15);
    const yStep = Math.ceil((bounds.maxY - bounds.minY) / 15);
    
    // Vertical grid lines
    for (let x = Math.ceil(bounds.minX); x <= bounds.maxX; x++) {
      const xPos = padding + ((x - bounds.minX) / (bounds.maxX - bounds.minX)) * effectiveWidth;
      
      // Draw grid line
      ctx.beginPath();
      ctx.moveTo(xPos, padding);
      ctx.lineTo(xPos, height - padding);
      ctx.strokeStyle = '#eee';
      ctx.stroke();

      // Add tick marks and numbers at steps
      if (x % xStep === 0) {
        // Draw tick mark
        ctx.beginPath();
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 2;
        ctx.moveTo(xPos, height - padding - 5);
        ctx.lineTo(xPos, height - padding + 5);
        ctx.stroke();

        // Draw number
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText(x.toString(), xPos, height - padding + 15);
      }
    }

    // Horizontal grid lines
    for (let y = Math.ceil(bounds.minY); y <= bounds.maxY; y++) {
      const yPos = padding + effectiveHeight - ((y - bounds.minY) / (bounds.maxY - bounds.minY)) * effectiveHeight;
      
      // Draw grid line
      ctx.beginPath();
      ctx.moveTo(padding, yPos);
      ctx.lineTo(width - padding, yPos);
      ctx.strokeStyle = '#eee';
      ctx.stroke();

      // Add tick marks and numbers at steps
      if (y % yStep === 0) {
        // Draw tick mark
        ctx.beginPath();
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 2;
        ctx.moveTo(padding - 5, yPos);
        ctx.lineTo(padding + 5, yPos);
        ctx.stroke();

        // Draw number
        ctx.fillStyle = '#666';
        ctx.textAlign = 'right';
        ctx.fillText(y.toString(), padding - 8, yPos + 4);
      }
    }

    // Draw split lines
    drawSplitLines(ctx, treeData, bounds);

    // Draw highlighted point
    if (highlightedPoint) {
      const x = padding + ((highlightedPoint.x - bounds.minX) / (bounds.maxX - bounds.minX)) * effectiveWidth;
      const y = padding + effectiveHeight - ((highlightedPoint.y - bounds.minY) / (bounds.maxY - bounds.minY)) * effectiveHeight;
      
      ctx.beginPath();
      ctx.fillStyle = '#2196f3';
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
    }

  }, [treeData, width, height, highlightedPoint, padding, effectiveWidth, effectiveHeight]);

  return (
    <Box sx={{ p: 2 }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onClick={handleCanvasClick}
        style={{ 
          border: '1px solid #ccc',
          borderRadius: '4px',
          cursor: 'crosshair'
        }}
      />
    </Box>
  );
};

export default CoordinateVisualization; 