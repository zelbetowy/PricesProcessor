package pl.matelcode.JavaServicesRunner;

import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;


@Component
public class ProviderRunner {

    private ArrayList<Process> processes  = new ArrayList<Process>();
    private final String pythonPath =  "../Portable Python-3.9.13 x64/App/Python/python.exe";



    public long startProcess(String scriptPath, ArrayList<String> args) {
        try {
            ProcessBuilder processBuilder = getProcessBuilder(scriptPath, args);
//            processBuilder.redirectOutput(ProcessBuilder.Redirect.INHERIT);
//            processBuilder.redirectError(ProcessBuilder.Redirect.INHERIT);
            Process process = processBuilder.start();
            processes.add(process);
            System.out.println("Python script started successfully.");
            return process.pid();

        } catch (IOException e) {
            System.err.println("Error Starting process: " + scriptPath + " " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        }
        return 0;
    }


    public void stopProcess(long PID) {
        ProcessHandle processHandle = ProcessHandle.of(PID).orElse(null);
        if (processHandle != null && processHandle.isAlive()) {
            // Zamknięcie wszystkich podprocesów
            processHandle.descendants().forEach(desc -> {
                if (desc.isAlive()) {
                    desc.destroy();
                    try {
                        desc.onExit().get(2, TimeUnit.SECONDS); // Poczekanie na zakończenie
                        System.out.println("Successfully terminated descendant of process " + PID);
                    } catch (Exception e) {
                        desc.destroyForcibly(); // Wymuszenie zamknięcia, jeśli nie zakończy się w czasie
                        System.out.println("Successfully forcibly terminated descendant of process " + PID);
                    }
                }
            });

            // Próba zamknięcia głównego procesu
            processHandle.destroy();
            try {
                processHandle.onExit().get(2, TimeUnit.SECONDS); // Poczekanie na zamknięcie głównego procesu
                if (processHandle.isAlive()) {
                    processHandle.destroyForcibly();
                    System.out.println("Successfully forcibly terminated main process " + PID);
                } else {
                    System.out.println("Main process " + PID + " terminated successfully.");
                }
            } catch (Exception e) {
                System.err.println("Failed to terminate main process " + PID);
                e.printStackTrace();
            }
        }

        else {
            System.out.println("Process with PID " + PID + " is not running");
        }
    }



    public void stopAllProcesses() {
        System.out.println(processes.toString());
        for (Process process : processes) {
            System.out.println(process.isAlive());
            if (process.isAlive()) {
                System.out.println("Attempting to close all instances of process");
                try {
                    // Zamknięcie wszystkich podprocesów
                    process.descendants().forEach(descendant -> {
                        if (descendant.isAlive()) {
                            descendant.destroy();
                            try {
                                descendant.onExit().get(5, TimeUnit.SECONDS); // Poczekanie
                                System.out.println("Successfully terminated a descendant process.");
                            } catch (Exception e) {
                                descendant.destroyForcibly(); // Wymuszenie zamknięcia
                                System.out.println("Forcibly terminated a descendant process.");
                            }
                        }
                    });

                    // Zamknięcie głównego procesu
                    process.getInputStream().close();
                    process.getErrorStream().close();
                    process.getOutputStream().close();
                    process.destroy();

                    if (process.isAlive()) {
                        process.destroyForcibly();
                        System.out.println("Main process was forcibly terminated.");
                    } else {
                        System.out.println("Main process terminated successfully.");
                    }
                }


                catch (IOException e) {
                    System.err.println("Failed to close streams for ExcelReader.");
                    e.printStackTrace();
                }
            } else {
                System.out.println("ExcelReader is not running.");
            }
        }
    }
}
