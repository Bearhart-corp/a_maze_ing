from window.visualizer import Window
import sys


def main() -> None:
    """verify the args and lauch the window"""
    if len(sys.argv) <= 1:
        print("put the path of the configuration\n"
              "For exemple: config.txt")
        exit(1)
    path = sys.argv[1]
    visualizer = Window(1000, 1000, "maze", path)
    visualizer.start()


if __name__ == "__main__":
    main()
