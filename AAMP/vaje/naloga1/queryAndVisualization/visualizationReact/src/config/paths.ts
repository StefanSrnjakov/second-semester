export const DATA_CONFIGS = {
  small: {
    name: 'Small Dataset (10MB)',
    files: {
      treeData: '/data/tree_small.txt',
      pointsData: '/data/points_small.bin'
    }
  },
  large: {
    name: 'Large Dataset (1.3GB)',
    files: {
      treeData: '/data/tree.txt',
      pointsData: '/data/points.bin' //2 mb
    }
  },
  large_big_chunks: {
    name: 'Large Dataset (1.3GB) with Big Chunks',
    files: {
      treeData: '/data/tree_big_chunks.txt',
      pointsData: '/data/points_big_chunks.bin' // 20mb
    }
  }
} as const;

export type DataConfigKey = keyof typeof DATA_CONFIGS; 