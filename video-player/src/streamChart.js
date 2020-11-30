import ApexCharts from "apexcharts";
import ReactApexChart from "react-apexcharts";

import { useEffect } from "react";

function getWidth(series) {
  const len = series.length;
  const widths = [];
  for (let i = 0; i < len - 1; i++) {
    widths.push(1);
  }
  widths.push(2);
  return widths;
}

function StreamChart({ id, series, type }) {
  const options = {
    chart: {
      id,
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
      selection: {
        enabled: false,
      },
      animations: {
        enabled: true,
        easing: "linear",
        speed: 20,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "straight",
      width: getWidth(series),
    },
    markers: {
      size: 0,
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      labels: {
        show: false,
      },
    },
    yaxis: {
      // tickAmount: 10
    },
    legend: {
      show: true,
    },
  };

  useEffect(() => {
    const cb = setInterval(() => {
      // options.yaxis.min = min(data)
      // options.yaxis.max = max(data)
      // ApexCharts.exec('realtime', 'updateOptions', options)
      ApexCharts.exec(id, "updateSeries", series);
    }, 100);
    return () => clearInterval(cb);
  }, [series]);

  return (
    <ReactApexChart
      options={options}
      series={series}
      type={type}
      height={150}
    />
  );
}

export default StreamChart;
