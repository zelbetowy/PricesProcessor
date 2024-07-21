package pl.matelcode.Kutarate;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PythonController {

    @GetMapping("/run-python-script")
    public String runPythonScript() {
        PyRunner runner = new PyRunner();
        try {
            runner.main(new String[]{});
        } catch (Exception e) {
            e.printStackTrace();
            return "Failed to run script.";
        }
        return "Script executed successfully.";
    }
}