from scripts.terminal import Terminal

def main():
    Terminal.clear()

if __name__ == "__main__":
    main()
else:
    raise RuntimeError("This project cannot be imported!")