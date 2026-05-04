package devxplaining.sentimentanalysis;

public class SentimentResult {

    private final String sentiment;
    private final int score;
    private final double confidence;

    public SentimentResult(String sentiment, int score) {
        this(sentiment, score, 0.0d);
    }

    public SentimentResult(String sentiment, int score, double confidence) {
        this.sentiment = sentiment;
        this.score = score;
        this.confidence = confidence;
    }

    public String getSentiment() {
        return sentiment;
    }

    public int getScore() {
        return score;
    }

    public double getConfidence() {
        return confidence;
    }

}