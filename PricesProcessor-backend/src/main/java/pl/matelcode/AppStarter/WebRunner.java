package pl.matelcode.AppStarter;

import jakarta.annotation.PreDestroy;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;
import pl.matelcode.AppStarter.PythonMicroServiceRunner.controller.PythonController;
import pl.matelcode.AppStarter.PythonMicroServiceRunner.service.PythonScriptsRunner;
import pl.matelcode.domains.symbol.service.SymbolService;

import java.util.ArrayList;
import java.util.Arrays;

@Service
public class WebRunner implements ProfileRunner {

    @Autowired
    private Environment environment; // Profile Check
    @Autowired
    private PythonScriptsRunner ProcessRunner;
    @Autowired
    private PythonController pythonController;
    @Autowired
    private SymbolService symbolService;

    @Autowired
    private HttpCaller httpcaller;



    @Override
    public void start() throws InterruptedException {
        String profile1 = "profile1";
        if (Arrays.asList(environment.getActiveProfiles()).contains(profile1)) {
            System.out.println("Profile: " + profile1);
            startServices();

        }
        else {System.out.println("No active profile detected.");}
    }


    public void startServices() throws InterruptedException {
        pythonController.runBaseBulid();
        Thread.sleep(5000);
//        ArrayList<String> stocks = symbolService.getAllTagFpMarketsByType("STOCK");
//        ArrayList<String> cryptos = symbolService.getAllTagFpMarketsByType("CRYPTOPAIR");
        ArrayList<String> cryptos = symbolService.getAllTagIcMarketsByType("CRYPTOPAIR");
        ArrayList<String> symbolsToProcess = new ArrayList<>();
//       symbolsToProcess.addAll(stocks);
        symbolsToProcess.addAll(cryptos);

//         Wsad dla MS1
        pythonController.setSymbolsToProcess(symbolsToProcess);
        httpcaller.callEndpointProvider( "http://localhost:8080/PythonApi/runPythonProvider", "config1");

        // Poczekajka na odpowiednią ilosc cen z providera
        Thread.sleep(15000);
        pythonController.runPricesThreatment();
    }



    @PreDestroy
    public void stop() {
        System.out.println("APP SHUTTING DOWN!");
        stopProviders();
    }

    public void stopProviders() {
        ProcessRunner.stopAllProcesses();
    }
}


//        ArrayList<String> cryptopairFp = symbolService.getAllTagFpMarketsByType("CRYPTOPAIR");
//        System.out.println(cryptopairFp.toString());
//        ArrayList<String> cryptopair = symbolService.getAllTagBinanceByType("CRYPTOPAIR");
//        System.out.println(cryptopair.toString());