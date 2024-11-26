package pl.matelcode.AppStarter.PythonMicroServiceRunner.controller;

import lombok.Getter;
import lombok.Setter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import pl.matelcode.AppStarter.PythonMicroServiceRunner.service.PythonScriptsRunner;
import pl.matelcode.domains.symbol.service.SymbolService;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/PythonApi")
public class PythonController {


//    @Autowired
//    private static final Logger logger = Logger.getLogger(PythonController.class.getName());

    @Autowired
    private PythonScriptsRunner pythonRunner;

    @Autowired
    private SymbolService symbolService;

    private String MS1path = "./Microservices/MS0_BaseBulid/BasebulidBackend.py";
    private String MS2path = "./Microservices/MS1_PricesProvider/ProcessSymbols.py";
    private String MS3path = "./Microservices/MS2_PricesThreatment/PricesThreatment.py";

    @Getter
    @Setter
    private ArrayList<String> symbolsToProcess;

    @Getter
    @Setter
    private Map<Long, ArrayList<String>> providerProcesses = new HashMap<>();
    private Map<Long, ArrayList<String>> threatmnentProcesses = new HashMap<>();



    @GetMapping("/runPythonProvider")
    public String runPythonProvider(@RequestParam("config") String config) {
        // sprwadzenie czy poprawnie wpisano "config1"
        if (!config.startsWith("config") || config.length() <= 6) {
            return "Invalid config format. Use configX, e.g., config1, config2.";
        }

        ArrayList<String> args = new ArrayList<>();
        args.add(config);
        args.addAll(symbolsToProcess);


        System.out.println("Uruchomiono proces z parametrami: " + args);
        long processPID = pythonRunner.startProcess(MS2path, args);
        // Zapisujemy PID, jeśli proces został uruchomiony poprawnie
        if (processPID != 0) {
            System.out.println("Uruchomiony PID: " + processPID);
            providerProcesses.put(processPID, args);

            return "Provider process + started with config: " + config;
        }
        return "";
    }


//    @EventListener(ApplicationReadyEvent.class)
    @GetMapping("/runBaseBulid")
    public String runBaseBulid() {
        System.out.println("LADOWANIE DANYCH DO BAZY");

        ArrayList<String> args = new ArrayList<>();
        long processPID = pythonRunner.startProcess(MS1path, args);
        if (processPID != 0) {
            providerProcesses.put(processPID, args);
        }
        return "";
    }


    @GetMapping("/stopProviders")
    public String stopProviders() {
        System.out.println();
        for (Long l : providerProcesses.keySet()) {
            pythonRunner.stopProcess(l);
        }
        return "All Providers stopped" ;
    }


    @GetMapping("/runPricesThreatment")
    public String runPricesThreatment() {
        ArrayList<String> args = new ArrayList<>();
        long processPID = pythonRunner.startProcess(MS3path,args);
        if (processPID != 0) {
            threatmnentProcesses.put(processPID, args);
        }
        String processPIDstring = "" + processPID;
        return processPIDstring;
    }
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