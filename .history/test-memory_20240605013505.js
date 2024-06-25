const v8 = require('v8');
console.log("Total Heap Size (GB):", (v8.getHeapStatistics().total_available_size / 1024 / 1024 / 1024).toFixed(2));