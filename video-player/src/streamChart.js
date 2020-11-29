import ApexCharts from "apexcharts";
import ReactApexChart from "react-apexcharts";
import min from "lodash/min";
import max from "lodash/max";

import { useEffect } from "react";

function StreamChart({ series }) {
  const options = {
    chart: {
      id: "realtime",
      height: 350,
      type: "line",
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
      width: 1,
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
    const id = setInterval(() => {
      // options.yaxis.min = min(data)
      // options.yaxis.max = max(data)
      // ApexCharts.exec('realtime', 'updateOptions', options)
      ApexCharts.exec("realtime", "updateSeries", series);
    }, 100);
    return () => clearInterval(id);
  }, [series]);

  return (
    <ReactApexChart
      options={options}
      series={series}
      type="line"
      height={350}
    />
  );
}

export default StreamChart;
