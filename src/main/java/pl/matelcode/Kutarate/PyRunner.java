package pl.matelcode.Kutarate;
import py4j.GatewayServer;
import java.io.IOException;


public class PyRunner {

    public static void main(String[] args) {
        try {
            // Uruchom skrypt Pythona
            ProcessBuilder pb = new ProcessBuilder("python", "D:/eduSoftware/Java/5. Kutarate/Kutarate/PythonScripts/PythonMT5/1MAIN.py");
            Process p = pb.start();

            // Czekaj na uruchomienie serwera Py4J
            Thread.sleep(5000);

            // Połącz się z GatewayServer
            GatewayServer gatewayServer = new GatewayServer();
            gatewayServer.start();
            PythonEntryPoint entryPoint = (PythonEntryPoint) gatewayServer.getPythonServerEntryPoint(new Class[]{PythonEntryPoint.class});

            // Wywołaj metodę run
            entryPoint.run();

            p.waitFor();

            gatewayServer.shutdown();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    public interface PythonEntryPoint {
        void run();
    }
}

