package pl.matelcode.PythonMicroservices;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import pl.matelcode.symbol.application.SymbolService;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

@RestController
@RequestMapping("/PythonApi")
public class PythonController {


//    @Autowired
//    private static final Logger logger = Logger.getLogger(PythonController.class.getName());

    @Autowired
    private PythonScriptsRunner pythonRunner;

    @Autowired
    private SymbolService symbolService;



    private String MS1path = "./Microservices/MS1_PricesProvider/1ProcessSymbols.py";
    private String MS2path = "./Microservices/MS2_PricesProvider/2ProcessSymbols.py";
    private String MS3path = "./Microservices/BaseBulid/basebulidBackend.py";



    private ArrayList<String> processSymbols1;
    private ArrayList<String> processSymbols2;

    private long ms1PID = 0;
    private long ms2PID = 0;
    private long ms3PID = 0;


    @GetMapping("/RUN_MS1")
    public String runMS1() {

        this.processSymbols1 = symbolService.getAllTagFpMarkets();
        System.out.println("WPISUJE DANE" + processSymbols1);
        long processPID = pythonRunner.startProcess(MS1path, processSymbols1);
        System.out.println(processPID);
        if (processPID != 0) {
            this.ms1PID = processPID;}
        return "";
    }

    @GetMapping("/RUN_MS2")
    public String runMS2() {
        this.processSymbols2 = symbolService.getAllTagIcMarkets();
        long processPID = pythonRunner.startProcess(MS2path, processSymbols2);
        if (processPID != 0) {
            ms2PID = processPID;}
        return "";
    }


    @EventListener(ApplicationReadyEvent.class)
    @GetMapping("/runBaseBulid")
    public String runBaseBulid() {
        System.out.println("LADOWANIE DANYCH DO BAZYY");

        ArrayList<String> args = new ArrayList<>();
        long processPID = pythonRunner.startProcess(MS3path,args);
        if (processPID != 0) {
            ms3PID = processPID;}
        return "";
    }


    @GetMapping("/STOP_MS1")
    public String stopMS1() {
        System.out.println(ms1PID);
        if (ms1PID != 0) {

            pythonRunner.stopProcess(ms1PID);
        }
        return ""+ms1PID ;
    }

    @GetMapping("/STOP_MS2")
    public String stopMS2() {
        System.out.println(ms2PID);
        if (ms2PID != 0) {
            pythonRunner.stopProcess(ms1PID);
        }
        return "";
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