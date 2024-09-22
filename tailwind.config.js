/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/app/*.html", "./templates/registration/*.html"],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}