from multiprocessing import Process

class APIHandler:

  def on_get(self, req, resp):
    heavy_process = Process(  # Create a daemonic process
        target=my_func,
        daemon=True
    )
    heavy_process.start()
    resp.body = "Quick response"

# Define some heavy function
def my_func():
    time.sleep(10)
    print("Process finished")