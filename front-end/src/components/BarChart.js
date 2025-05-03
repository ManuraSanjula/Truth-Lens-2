"use client";

import {
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const BarChart = () => {
    const data = {
        labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
        datasets: [
            {
                label: "Trending Data",
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: "rgba(53, 162, 235, 0.5)",
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: "top",
            },
            title: {
                display: true,
            },
        },
    };

    return <Bar data={data} options={options} />;
};

export default BarChart;