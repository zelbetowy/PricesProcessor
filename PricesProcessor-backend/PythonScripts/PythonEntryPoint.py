from py4j.java_gateway import JavaGateway, CallbackServerParameters

class PythonEntryPoint:
    def run(self):
        print("Python code is running")
        return "Python code has run"

if __name__ == "__main__":
    entry_point = PythonEntryPoint()
    gateway = JavaGateway(
        callback_server_parameters=CallbackServerParameters(port=8090),
        python_server_entry_point=entry_point
    )
    print("Gateway Server Started")
    print("CallbackServerParameters: " + str(CallbackServerParameters()))
    gateway.entry_point.run()
    print("PythonEntryPoint.run() executed")