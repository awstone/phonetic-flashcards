import gradio as gr 

def test_no_output(inputs):
    gr.Textbox('weeee')
    

with gr.Blocks() as demo:

    textbox = gr.Textbox('input text')
    button = gr.Button()
    button.click(test_no_output, textbox)

demo.launch()


