import { Box, Container, TextField, Typography, Paper, Button, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useState } from 'react';
import { searchCoordinates, SearchResult } from './coordinateSearch';
import TreeVisualization from './components/TreeVisualization';
import { DATA_CONFIGS, DataConfigKey } from './config/paths';
import CoordinateVisualization from './components/CoordinateVisualization';

const App = () => {
  const [coordinates, setCoordinates] = useState({
    x: '',
    y: ''
  });
  const [result, setResult] = useState<SearchResult | null>(null);
  const [dataConfig, setDataConfig] = useState<DataConfigKey>('small');
  const [treeData, setTreeData] = useState<any>(null);

  const handleCoordinateChange = (field: 'x' | 'y') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setCoordinates(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    setResult(null);
  };

  const handleSearch = async () => {
    if (coordinates.x && coordinates.y) {
      try {
        const searchResult = await searchCoordinates(
          coordinates.x, 
          coordinates.y, 
          DATA_CONFIGS[dataConfig].files
        );
        setResult(searchResult);
      } catch (error) {
        console.error('Search failed:', error);
      }
    }
  };

  const handleCoordinateClick = (x: number, y: number) => {
    const newCoordinates = {
      x: x.toString(),
      y: y.toString()
    };
    setCoordinates(newCoordinates);
    
    // Search with the new coordinates directly instead of using state
    searchCoordinates(
      newCoordinates.x,
      newCoordinates.y,
      DATA_CONFIGS[dataConfig].files
    ).then(searchResult => {
      setResult(searchResult);
    }).catch(error => {
      console.error('Search failed:', error);
    });
  };

  return (
    <Container maxWidth="xl" sx={{ p: 0 }}>
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* Left Panel */}
        <Box sx={{ width: 500, p: 3, borderRight: 1, borderColor: 'divider' }}>
          <Typography variant="h4" gutterBottom>
            Coordinate Search
          </Typography>
          
          {/* Dataset Selection */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Dataset Size</InputLabel>
              <Select
                value={dataConfig}
                label="Dataset Size"
                onChange={(e) => setDataConfig(e.target.value as DataConfigKey)}
              >
                {Object.entries(DATA_CONFIGS).map(([key, config]) => (
                  <MenuItem key={key} value={key}>
                    {config.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Paper>

          {/* Search Panel */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Search Coordinates
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="X"
                value={coordinates.x}
                onChange={handleCoordinateChange('x')}
                type="number"
                inputProps={{ step: 'any' }}
                fullWidth
              />
              <TextField
                label="Y"
                value={coordinates.y}
                onChange={handleCoordinateChange('y')}
                type="number"
                inputProps={{ step: 'any' }}
                fullWidth
              />
              <Button 
                variant="contained" 
                onClick={handleSearch}
                disabled={!coordinates.x || !coordinates.y}
              >
                Search
              </Button>
            </Box>
          </Paper>

          {/* Results Panel */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Results
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              gap: 1
            }}>
              {result !== null && (
                <>
                  <Typography variant="h5">
                    Nearest Point
                  </Typography>
                  <Typography variant="h5">
                    X = {result.x}
                  </Typography>
                  <Typography variant="h5">
                    Y = {result.y}
                  </Typography>
                  <Typography variant="h5">
                    Z = {result.z}
                  </Typography>
                  <Typography variant="h5">
                    Time to find chunk: {result.timeToFindChunk?.toFixed(2)} ms
                  </Typography>
                  <Typography variant="h5">
                    Time to find point: {result.timeToFindPoint?.toFixed(2)} ms
                  </Typography>
                  <Typography variant="h5">
                    Total time: {result.totalTime?.toFixed(2)} ms
                  </Typography>
                </>
              )}
            </Box>
          </Paper>
        </Box>

        {/* Right Panel */}
        <Box sx={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          p: 3,  // Add padding
          gap: 3  // Add gap between visualizations
        }}>
          {/* Coordinate Visualization */}
          <Paper 
            elevation={2} 
            sx={{ 
              height: '500px',  // Increased height
              p: 2,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Typography variant="h6" gutterBottom>
              Coordinate Space
            </Typography>
            <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
              <CoordinateVisualization 
                treeData={treeData}
                highlightedPoint={result ? { x: result.x, y: result.y } : undefined}
                width={600}
                height={400}
                onCoordinateClick={handleCoordinateClick}
              />
            </Box>
          </Paper>

          {/* Tree Visualization */}
          <Paper 
            elevation={2} 
            sx={{ 
              flex: 1,
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
          >
            <Typography variant="h6" gutterBottom>
              Tree Structure
            </Typography>
            <Box sx={{ flex: 1 }}>
              <TreeVisualization 
                x={coordinates.x} 
                y={coordinates.y} 
                config={DATA_CONFIGS[dataConfig].files}
                onTreeLoad={setTreeData}
              />
            </Box>
          </Paper>
        </Box>
      </Box>
    </Container>
  );
};

export default App; 