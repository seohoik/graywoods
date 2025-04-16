/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{astro,html,js,jsx,ts,tsx,vue,svelte}',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  // DaisyUI 옵션 설정 (원하는 테마 커스터마이징이 가능)
  daisyui: {
    themes: ["light", "dark"],  // 기본적으로 제공되는 테마 목록을 설정
  },
};
