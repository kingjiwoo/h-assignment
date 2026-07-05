/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // vega-canvas ships a node-only fallback that imports 'canvas' when it can't
  // find a browser Canvas. In our browser-only usage we never hit that branch,
  // so we alias it to false to silence the "Module not found: canvas" warning.
  webpack(config) {
    config.resolve = config.resolve ?? {};
    config.resolve.alias = { ...(config.resolve.alias ?? {}), canvas: false };
    return config;
  },
};

export default nextConfig;
