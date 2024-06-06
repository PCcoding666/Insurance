# main.py
from gradio_interface import create_interface

def main():
    demo = create_interface()
    demo.launch(share=True)

if __name__ == "__main__":
    main()
