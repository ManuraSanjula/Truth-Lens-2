import withFlowbiteReact from "flowbite-react/plugin/nextjs";

/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "assets.aceternity.com",
                port: "",
                pathname: "/**",
            },
            {
                protocol: "https",
                hostname: "**",
                port: "",
                pathname: "/**",
            },
            {
                protocol: "https",
                hostname: "flowbite.com",
                port: "",
                pathname: "/**",
            },
            {
                protocol: "https",
                hostname: "flowbite-react.com",
                port: "",
                pathname: "/**",
            },
        ],
    },
};

export default withFlowbiteReact(nextConfig);