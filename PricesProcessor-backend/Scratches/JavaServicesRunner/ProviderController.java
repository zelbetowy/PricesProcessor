package pl.matelcode.JavaServicesRunner;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/ProviderAPI")
public class ProviderController {

    @Autowired
    ProviderRunner providerRunner;

    private  Map<String, Provider> providers = new HashMap<>();




    @PostMapping("/startProvide")
    public String createProvider(@RequestParam String symbol, @RequestParam long interval) {
        if (providers.containsKey(symbol)) {
            return "Provider dla symbolu " + symbol + " już istnieje.";
        }

        Provider provider = new Provider(symbol, interval);
        providers.put(symbol, provider);
        provider.startProviding();
        return "Utworzono i uruchomiono providera dla symbolu " + symbol + " z interwałem " + interval + " ms.";
    }

//    @PostMapping("/stop")
//    public String stopProviding() {
//        try {
//            provider.stopProviding();
//            return "Proces dostarczania danych został zatrzymany.";
//        } catch (Exception e) {
//            return "Błąd przy zatrzymywaniu procesu: " + e.getMessage();
//        }
//    }

}










//    @GetMapping("/run-python-2ProcessSymbols")
//    public String runPythonScript2ProcessSymbols() {
//        try {
//            if (pythonProcess2ProcessSymbols == null || !pythonProcess2ProcessSymbols.isAlive()) {
//                ProcessBuilder processBuilder = new ProcessBuilder(
//                        "cmd.exe", "/c", "start", "cmd.exe", "/k", "python ./Microservices/MS1_PricesProvider/2ProcessSymbols.py"
//                );
//                pythonProcess2ProcessSymbols = processBuilder.start();
//                logger.info("Python script 2ProcessSymbols started successfully.");
//                return "Python script 2ProcessSymbols started successfully.";
//            } else {
//                logger.warning("Python script 2ProcessSymbols is already running.");
//                return "Python script 2ProcessSymbols is already running.";
//            }
//        } catch (IOException e) {
//            logger.severe("Failed to start script 2ProcessSymbols: " + e.getMessage());
//            e.printStackTrace();
//            return "Failed to start script 2ProcessSymbols.";
//        }
//    }
//    @GetMapping("/stop-python-2ProcessSymbols")
//    public String stopPythonScript2ProcessSymbols() {
//        if (pythonProcess2ProcessSymbols != null && pythonProcess2ProcessSymbols.isAlive()) {
//            pythonProcess2ProcessSymbols.destroy();
//            logger.info("Python script 2ProcessSymbols stopped successfully.");
//            return "Python script 2ProcessSymbols stopped successfully.";
//        } else {
//            logger.warning("Python script 2ProcessSymbols is not running.");
//            return "Python script 2ProcessSymbols is not running.";
//        }
//    }
//
//
//
//    @GetMapping("/run-python-3ExtrapolateSymbols")
//    public String runpython3ExtrapolateSymbols() {
//        try {
//            if (pythonprocess3ExtrapolateSymbols == null || !pythonprocess3ExtrapolateSymbols.isAlive()) {
//                ProcessBuilder processBuilder = new ProcessBuilder(
//                        "cmd.exe", "/c", "start", "cmd.exe", "/k", "python D:/#SOFT/JAVA/Kutarate/Kutarate/PythonScripts/SymbolProcessor/3ExtrapolateSymbols.py"
//                );
//                pythonprocess3ExtrapolateSymbols = processBuilder.start();
//                logger.info("Python script 3ExtrapolateSymbols started successfully.");
//                return "Python script 2ProcessSymbols started successfully.";
//            } else {
//                logger.warning("Python script 3ExtrapolateSymbols is already running.");
//                return "Python script 3ExtrapolateSymbols is already running.";
//            }
//        } catch (IOException e) {
//            logger.severe("Failed to start script 3ExtrapolateSymbols: " + e.getMessage());
//            e.printStackTrace();
//            return "Failed to start script 3ExtrapolateSymbols.";
//        }
//    }
//    @GetMapping("/stop-python-3ExtrapolateSymbols")
//    public String stoppython3ExtrapolateSymbols() {
//        if (pythonprocess3ExtrapolateSymbols != null && pythonprocess3ExtrapolateSymbols.isAlive()) {
//            pythonprocess3ExtrapolateSymbols.destroy();
//            logger.info("Python script 3ExtrapolateSymbols stopped successfully.");
//            return "Python script 2ProcessSymbols stopped successfully.";
//        } else {
//            logger.warning("Python script 3ExtrapolateSymbols is not running.");
//            return "Python script 2ProcessSymbols is not running.";
//        }
//    }
//
//
//    @GetMapping("/run-python-1FetchHistoricalData")
//    public String runPythonScript1FetchHistoricalData() {
//        try {
//            if (pythonProcess1FetchHistoricalData == null || !pythonProcess1FetchHistoricalData.isAlive()) {
//                ProcessBuilder processBuilder = new ProcessBuilder(
//                        "cmd.exe", "/c", "start", "cmd.exe", "/k", "python D:/#SOFT/JAVA/Kutarate/Kutarate/PythonScripts/SymbolProcessor/1FetchHistoricalData.py"
//                );
//                pythonProcess1FetchHistoricalData = processBuilder.start();
//                logger.info("Python script 1FetchHistoricalData started successfully.");
//                return "Python script 1FetchHistoricalData started successfully.";
//            } else {
//                logger.warning("Python script 1FetchHistoricalData is already running.");
//                return "Python script 1FetchHistoricalData is already running.";
//            }
//        } catch (IOException e) {
//            logger.severe("Failed to start script 1FetchHistoricalData: " + e.getMessage());
//            e.printStackTrace();
//            return "Failed to start script 1FetchHistoricalData.";
//        }
//    }
//
//
//    @GetMapping("/run-python")
//    public String runPythonScript() {
//        if (pythonProcessHelloWorld != null && pythonProcessHelloWorld.isAlive()) {
//            logger.warning("Python script is already running.");
//            return "Python script is already running.";
//        }
//
//        try {
//            ProcessBuilder processBuilder = new ProcessBuilder(
//                    "cmd.exe", "/c", "start", "cmd.exe", "/k", "python D:/#SOFT/JAVA/Kutarate/Kutarate/PythonScripts/hello_world.py"
//            );
//            pythonProcessHelloWorld = processBuilder.start();
//            logger.info("Python script started.");
//            return "Python script started.";
//        } catch (IOException e) {
//            logger.severe("Failed to start Python script: " + e.getMessage());
//            e.printStackTrace();
//            return "Failed to start Python script: " + e.getMessage();
//        }
//    }
//    @GetMapping("/stop-python")
//    public String stopPythonScript() {
//        if (pythonProcessHelloWorld != null && pythonProcessHelloWorld.isAlive()) {
//            pythonProcessHelloWorld.destroy();
//            logger.info("Python script stopped.");
//            return "Python script stopped.";
//        } else {
//            logger.warning("Python script is not running.");
//            return "Python script is not running.";
//        }
//    }
//}