// import { digl } from window.crinkles;
const digl = window.crinkles.digl;

const machine = digl({ shortestPath: false, addEmptySpots: true });
const nodes = [{id: 0}, {id: 1}, {id: 2}, {id: 3}, {id: 4}, {id: 5}, {id: 6}, {id: 10}];
const edges = [
  { source: '0', target: '1' },
  { source: '0', target: '2' },
  { source: '0', target: '5' },
  { source: '5', target: '6' },
  { source: '2', target: '3' },
  { source: '2', target: '4' }, 
  { source: '6', target: '10' }, 
  { source: '1', target: '10' }, 
  { source: '3', target: '10' }, 
  { source: '4', target: '10' }, 
];

// const ranks = machine.get('0', edges);
// console.log(ranks)
// // [['1'], ['2']]
// const score = machine.score('0', edges);
// console.log(score)
// // 0

function positioning(
    config,
    nodes,
    ranks
  ) {
    const _nodes = [];
    const _h = config.orientation === 'horizontal';
  
    ranks.forEach((r, i) => {
      const xStart = _h
        ? 2 * config.width * i + config.x_offset
        : -0.5 * (r.length - 1) * 2 * config.width + config.x_offset;
      const yStart = _h
        ? -0.5 * (r.length - 1) * 2 * config.height
        : 2 * config.height * i;
  
      r.forEach((nodeId, nIndex) => {
        const _node = nodes.find((n) => n.id == nodeId);
        if (!_node) return;
        const x = _h ? xStart : xStart + 2 * config.width * nIndex;
        const y = _h ? yStart + 2 * config.height * nIndex : yStart;
        _nodes.push({ ..._node, x, y });
      });
    });
  
    return _nodes;
  }

export default function layout_alg(nodes, edges) {
  // nodes: [{id: }, ]
  // edges: [{source: id, target: id}, ]
  const start_id = 0;
  const end_id = 10;
  const x_dist = 20;
  const y_dist = 20;
  const x_offset = -10;



  const machine = digl({ shortestPath: false, addEmptySpots: true });
  const ranks = machine.get('0', edges);

  const config = {  width: 1, 
                    height: 1,
                    orientation: 'horizontal', 
                    x_offset: x_offset };
  let pos = positioning(config, nodes, ranks);
  
  const x_range = pos.find(item => item.id === end_id).x - pos.find(item => item.id === start_id).x;
  const y_offset = Math.min(...pos.map(o => o.y));
  const y_range = Math.max(...pos.map(o => o.y)) - y_offset;
  const x_scale = x_dist / x_range;
  const y_scale = y_dist / y_range;

  let result = {};
  pos.forEach(function(item) { 
    result[item.id] = { 
      x: ((item.x - x_offset) * x_scale) + x_offset,
      y: ((item.y - y_offset) * y_scale) - y_dist / 2
    };
  });
  
  return result;
}

// console.log(layout_alg(nodes, edges))
