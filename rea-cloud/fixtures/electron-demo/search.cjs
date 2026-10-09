const items = ['cloud', 'codex', 'reverse engineering'];

exports.searchItems = function searchItems(query) {
  return items.filter((item) => item.includes(String(query).toLowerCase()));
};
