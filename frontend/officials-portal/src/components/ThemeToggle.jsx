import { Moon, Sun } from "lucide-react"
import { useTheme } from "./ThemeProvider"

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      {theme === "light" ? (
        <Moon className="h-5 w-5 text-gray-600" />
      ) : (
        <Sun className="h-5 w-5 text-gray-300" />
      )}
    </button>
  )
}

export default ThemeToggle
