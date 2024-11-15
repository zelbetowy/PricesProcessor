package pl.matelcode.AppStarter;

import jakarta.annotation.PreDestroy;
import lombok.Getter;
import lombok.Setter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;
import pl.matelcode.PythonMicroservices.PythonScriptsRunner;

import java.util.Arrays;

@Service
public class WebRunner implements ProfileRunner {

    @Getter
    @Setter
    private String [] ScriptsPaths = {
              "./Microservices/MS2_PricesThreatment/excel_reader.py"
            , "./Microservices/MS2_PricesThreatment/excel_reader.py"
    };

    @Autowired
    private Environment environment; // Profile Check

    @Autowired
    private PythonScriptsRunner ProcessRunner;

    @Override
    public void start() {


        String profile1 = "profile1";
        if (Arrays.asList(environment.getActiveProfiles()).contains(profile1)) {
            System.out.println("Profile: " + profile1);
        } else {
            System.out.println("No active profile detected.");
        }
    }



    @PreDestroy
    public void stop() {
        System.out.println("APP SHUTTING DOWN!");
        stopServices();
    }


    public void stopServices() {
        ProcessRunner.stopAllProcesses();
    }
}
