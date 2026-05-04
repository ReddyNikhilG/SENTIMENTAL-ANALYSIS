package devxplaining.sentimentanalysis;

import ai.djl.Application;
import ai.djl.Device;
import ai.djl.inference.Predictor;
import ai.djl.modality.Classifications;
import ai.djl.repository.zoo.Criteria;
import ai.djl.repository.zoo.ZooModel;
import ai.djl.training.util.ProgressBar;
import org.springframework.stereotype.Service;

import jakarta.annotation.PreDestroy;
import java.io.IOException;

@Service
public class SentimentService {

    private static final String MODEL_NAME = "DistilBERT Sentiment Classifier";
    private static final String MODEL_DESCRIPTION =
        "A locally loaded transformer sentiment model fine-tuned with PyTorch. It predicts positive and negative probabilities, with a neutral label inferred when the scores are close together.";
    private static final String MODEL_TECH = "djl://ai.djl.pytorch/distilbert";

    private final ZooModel<String, Classifications> model;
    private final Predictor<String, Classifications> predictor;

    public SentimentService() {
        try {
            Criteria<String, Classifications> criteria = Criteria.builder()
                .setTypes(String.class, Classifications.class)
                .optApplication(Application.NLP.SENTIMENT_ANALYSIS)
                .optModelUrls(MODEL_TECH)
                .optEngine("PyTorch")
                .optDevice(Device.cpu())
                .optProgress(new ProgressBar())
                .build();

            this.model = criteria.loadModel();
            this.predictor = model.newPredictor();
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to load the DistilBERT sentiment model", exception);
        }
    }

    public String getModelName() {
        return MODEL_NAME;
    }

    public String getModelDescription() {
        return MODEL_DESCRIPTION;
    }

    public String getModelTech() {
        return MODEL_TECH;
    }

    public SentimentResult analyze(String text) {
        if (text == null || text.isBlank()) {
            return new SentimentResult("Neutral", 2, 0.0d);
        }

        try {
            Classifications classifications = predictor.predict(text);
            double positiveProbability = probabilityFor(classifications, "Positive");
            double negativeProbability = probabilityFor(classifications, "Negative");
            double confidence = Math.max(positiveProbability, negativeProbability);

            String sentiment;
            int score;
            if (Math.abs(positiveProbability - negativeProbability) < 0.15d) {
                sentiment = "Neutral";
                score = 2;
            } else if (positiveProbability > negativeProbability) {
                sentiment = "Positive";
                score = Math.max(0, Math.min(4, (int) Math.round(((positiveProbability - negativeProbability) + 1.0d) * 2.0d)));
            } else {
                sentiment = "Negative";
                score = Math.max(0, Math.min(4, (int) Math.round(((positiveProbability - negativeProbability) + 1.0d) * 2.0d)));
            }

            return new SentimentResult(sentiment, score, confidence);
        } catch (Exception exception) {
            return new SentimentResult("Neutral", 2, 0.0d);
        }
    }

    private double probabilityFor(Classifications classifications, String label) {
        return classifications.items().stream()
            .filter(item -> item.getClassName().equalsIgnoreCase(label))
            .mapToDouble(Classifications.Classification::getProbability)
            .findFirst()
            .orElse(0.0d);
    }

    @PreDestroy
    public void shutdown() {
        try {
            predictor.close();
        } catch (Exception ignored) {
            // Ignore shutdown issues.
        }

        try {
            model.close();
        } catch (Exception ignored) {
            // Ignore shutdown issues.
        }
    }
}
