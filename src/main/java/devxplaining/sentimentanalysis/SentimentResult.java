package devxplaining.sentimentanalysis;

public class SentimentResult {

    private final String sentiment;
    private final int score;

    public SentimentResult(String sentiment, int score) {
        this.sentiment = sentiment;
        this.score = score;
    }

    public String getSentiment() {
        return sentiment;
    }

    public int getScore() {
        return score;
    }

}