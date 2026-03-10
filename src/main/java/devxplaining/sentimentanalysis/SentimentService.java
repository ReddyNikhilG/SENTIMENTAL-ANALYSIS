package devxplaining.sentimentanalysis;

import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sentiment.SentimentCoreAnnotations;
import edu.stanford.nlp.util.CoreMap;
import org.springframework.stereotype.Service;

import java.util.Properties;

@Service
public class SentimentService {

    private StanfordCoreNLP pipeline;

    public SentimentService(){

        Properties props = new Properties();
        props.setProperty("annotators","tokenize,ssplit,parse,sentiment");

        pipeline = new StanfordCoreNLP(props);
    }

    public SentimentResult analyze(String text){
        if (text == null || text.isBlank()) {
            return new SentimentResult("Neutral", 2);
        }

        Annotation annotation = pipeline.process(text);

        var sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
        if (sentences == null || sentences.isEmpty()) {
            return new SentimentResult("Neutral", 2);
        }

        int totalScore = 0;
        int sentenceCount = 0;

        for(CoreMap sentence : sentences){
            int sentenceScore = edu.stanford.nlp.neural.rnn.RNNCoreAnnotations
                .getPredictedClass(
                    sentence.get(SentimentCoreAnnotations.SentimentAnnotatedTree.class));
            totalScore += sentenceScore;
            sentenceCount++;
        }

        int averageScore = Math.round((float) totalScore / sentenceCount);
        String sentiment = switch (averageScore) {
            case 0 -> "Very Negative";
            case 1 -> "Negative";
            case 2 -> "Neutral";
            case 3 -> "Positive";
            case 4 -> "Very Positive";
            default -> "Neutral";
        };

        return new SentimentResult(sentiment, averageScore);
    }

}