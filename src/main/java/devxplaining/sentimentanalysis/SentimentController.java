package devxplaining.sentimentanalysis;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Controller
public class SentimentController {

    private static final int MAX_HISTORY = 50;
    private static final DateTimeFormatter HISTORY_TIME_FORMATTER =
        DateTimeFormatter.ofPattern("dd MMM yyyy, hh:mm a");

    private final SentimentService service;
    private final List<Map<String, String>> history =
        Collections.synchronizedList(new ArrayList<>());

    public SentimentController(SentimentService service) {
        this.service = service;
    }

    private void addSharedModelAttributes(Model model) {
        model.addAttribute("modelName", service.getModelName());
        model.addAttribute("modelDescription", service.getModelDescription());
        model.addAttribute("modelTech", service.getModelTech());
    }


    // Homepage
    @GetMapping("/")
    public String home(Model model){

        addSharedModelAttributes(model);
        model.addAttribute("history", history);
        model.addAttribute("currentText", "");
        model.addAttribute("sentiment", "Neutral");
        model.addAttribute("score", 2);
        model.addAttribute("emoji", "😐");
        model.addAttribute("confidenceText", "0%");

        return "index";
    }


    // Analyze sentiment when form is submitted
    @PostMapping("/analyze")
    public String analyze(@RequestParam("text") String text, Model model){

        addSharedModelAttributes(model);

        if (text == null || text.isBlank()) {
            model.addAttribute("error", "Please enter some text to analyze.");
            model.addAttribute("history", history);
            model.addAttribute("currentText", "");
            return "index";
        }

        if (text.length() > 5000) {
            model.addAttribute("error", "Text is too long. Please keep it under 5000 characters.");
            model.addAttribute("history", history);
            model.addAttribute("currentText", text);
            return "index";
        }

        SentimentResult result = service.analyze(text);

        String emoji = "😐";

        if(result.getSentiment().contains("Positive")){
            emoji = "😊";
        }

        if(result.getSentiment().contains("Negative")){
            emoji = "😡";
        }

        Map<String, String> record = new HashMap<>();

        record.put("text", text);
        record.put("sentiment", result.getSentiment());
        record.put("score", String.valueOf(result.getScore()));
        record.put("emoji", emoji);
        record.put("createdAt", LocalDateTime.now().format(HISTORY_TIME_FORMATTER));

        synchronized (history) {
            history.add(0, record);
            if (history.size() > MAX_HISTORY) {
                history.remove(history.size() - 1);
            }
        }

        model.addAttribute("sentiment", result.getSentiment());
        model.addAttribute("score", result.getScore());
        model.addAttribute("emoji", emoji);
        model.addAttribute("confidenceText", Math.round(result.getConfidence() * 100) + "%");
        model.addAttribute("history", history);
        model.addAttribute("currentText", text);

        return "index";
    }


    // Live sentiment API (used while typing)
    @GetMapping("/live")
    @ResponseBody
    public Map<String,String> live(@RequestParam String text){

        if (text == null || text.isBlank()) {
            return Map.of(
                "sentiment", "Neutral",
                "score", "2",
                "emoji", "😐",
                "confidenceText", "0%"
            );
        }

        SentimentResult result = service.analyze(text);
        String emoji = "😐";
        if (result.getSentiment().contains("Positive")) {
            emoji = "😊";
        }
        if (result.getSentiment().contains("Negative")) {
            emoji = "😡";
        }

        return Map.of(
            "sentiment", result.getSentiment(),
            "score", String.valueOf(result.getScore()),
            "emoji", emoji,
            "confidenceText", Math.round(result.getConfidence() * 100) + "%"
        );
    }

}