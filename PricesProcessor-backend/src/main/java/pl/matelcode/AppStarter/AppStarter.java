package pl.matelcode.AppStarter;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Getter
@Component
public class AppStarter {

    @Autowired
    private final ProfileRunner profileRunner;


    public AppStarter(ProfileRunner profileRunner) {
        this.profileRunner = profileRunner;
    }


    // After Start SPRING
    @EventListener(ApplicationReadyEvent.class)
    public void start() throws InterruptedException {

        System.out.println("=====================================");
        System.out.println("Welcome to Prices Monitor!");
        System.out.println("Running on Java version: " + System.getProperty("java.version"));
        System.out.println("=====================================");
        System.out.println("Java home: " + System.getProperty("java.home"));
        System.out.println("Java vendor URL: " + System.getProperty("java.vendor.url"));
        System.out.println();

        System.out.println("OS name: " + System.getProperty("os.name"));
        System.out.println("OS version: " + System.getProperty("os.version"));
        System.out.println("OS architecture: " + System.getProperty("os.arch"));
        System.out.println("User name: " + System.getProperty("user.name"));
        System.out.println("Current working directory: " + System.getProperty("user.dir"));
        System.out.println();

        System.out.println("File separator: " + System.getProperty("file.separator"));
        System.out.println("Path separator: " + System.getProperty("path.separator"));

        profileRunner.start();
    }
}
