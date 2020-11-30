export function append(data: number[], x: number, maxChartTicks: number) {
  data.push(x);
  if (data.length > maxChartTicks) {
    data.splice(0, data.length - maxChartTicks);
  }
}
