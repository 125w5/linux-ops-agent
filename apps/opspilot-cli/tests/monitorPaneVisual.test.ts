import { expect, test } from 'bun:test'
import {
  diskLabel,
  loadLabel,
  memoryLabel,
  percentLabel,
  processRows,
  sparkline,
  usageBar,
} from '../src/utils/resourceFormat.js'

test('formats monitor usage bars and process lists', () => {
  const system = {
    cpu_percent: 68,
    memory_percent: 24,
    memory_used_gb: 1.2,
    memory_total_gb: 5.0,
    load_average: [0.08, 0.12, 0.1],
  }
  const disk = { mountpoint: 'C:', used_gb: 142, total_gb: 210, percent: 67.6 }
  const topCpu = processRows([{ name: 'python.exe', cpu_percent: 12.1 }])
  const topMem = processRows([{ name: 'chrome.exe', memory_mb: 812 }], 5)

  expect(usageBar(system.cpu_percent)).toBe('███████░░░')
  expect(percentLabel(disk.percent)).toBe('68%')
  expect(loadLabel(system.load_average)).toBe('load 0.08 0.12 0.10')
  expect(memoryLabel(system)).toBe('1.2G / 5.0G')
  expect(diskLabel(disk)).toBe('C: 142G / 210G')
  expect(topCpu[0].name).toBe('python.exe')
  expect(topCpu[0].cpuPercent).toBe(12.1)
  expect(topMem[0].memoryMb).toBe(812)
  expect(sparkline([7, 24, 68])).toContain('▆')
})
