#!/usr/bin/env python3
"""
Sentiment Analysis Web Application
A simple Flask-based web interface for analyzing text sentiment
"""

from flask import Flask, render_template_string, request, jsonify
import re
from collections import Counter

app = Flask(__name__)

# Simple sentiment lexicon (can be expanded)
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love',
    'happy', 'joy', 'beautiful', 'perfect', 'best', 'awesome', 'brilliant',
    'outstanding', 'superb', 'terrific', 'nice', 'positive', 'fortunate',
    'correct', 'superior', 'delightful', 'enjoyed', 'liking', 'pleasure',
    'success', 'successful', 'victory', 'win', 'triumph', 'celebrate'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'sad', 'angry',
    'disgusting', 'poor', 'negative', 'unfortunate', 'wrong', 'inferior',
    'disappointing', 'disappointed', 'boring', 'ugly', 'failure', 'fail',
    'lose', 'lost', 'defeat', 'disaster', 'catastrophe', 'annoying', 'upset',
    'depressing', 'miserable', 'pathetic', 'useless', 'waste'
}

# Intensifiers and negations
INTENSIFIERS = {'very', 'extremely', 'incredibly', 'absolutely', 'totally', 'really', 'so'}
NEGATIONS = {'not', 'no', 'never', 'neither', 'nobody', 'nothing', "n't", 'none'}

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text
    Returns: dict with sentiment score, label, and details
    """
    if not text or not text.strip():
        return {
            'score': 0,
            'label': 'Neutral',
            'confidence': 0,
            'positive_words': [],
            'negative_words': [],
            'word_count': 0
        }
    
    # Preprocess text
    text_lower = text.lower()
    # Simple tokenization
    words = re.findall(r'\b\w+\b', text_lower)
    
    positive_score = 0
    negative_score = 0
    found_positive = []
    found_negative = []
    
    # Analyze with context
    for i, word in enumerate(words):
        # Check for negation in previous 2 words
        negated = False
        if i > 0 and words[i-1] in NEGATIONS:
            negated = True
        elif i > 1 and words[i-2] in NEGATIONS:
            negated = True
        
        # Check for intensifier in previous word
        intensified = False
        if i > 0 and words[i-1] in INTENSIFIERS:
            intensified = True
        
        # Calculate score with modifiers
        multiplier = 1.5 if intensified else 1.0
        
        if word in POSITIVE_WORDS:
            if negated:
                negative_score += multiplier
                found_negative.append(f"not {word}")
            else:
                positive_score += multiplier
                found_positive.append(word)
        elif word in NEGATIVE_WORDS:
            if negated:
                positive_score += multiplier
                found_positive.append(f"not {word}")
            else:
                negative_score += multiplier
                found_negative.append(word)
    
    # Calculate final sentiment
    total_score = positive_score - negative_score
    max_possible = max(positive_score + negative_score, 1)  # Avoid division by zero
    
    # Normalize score to -1 to 1 range
    normalized_score = total_score / max_possible if max_possible > 0 else 0
    
    # Determine label and confidence
    if normalized_score > 0.1:
        label = 'Positive'
        confidence = min(abs(normalized_score) * 100, 100)
    elif normalized_score < -0.1:
        label = 'Negative'
        confidence = min(abs(normalized_score) * 100, 100)
    else:
        label = 'Neutral'
        confidence = 100 - min(abs(normalized_score) * 100, 100)
    
    return {
        'score': round(normalized_score, 3),
        'label': label,
        'confidence': round(confidence, 1),
        'positive_words': list(set(found_positive)),
        'negative_words': list(set(found_negative)),
        'word_count': len(words)
    }

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analysis Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .input-section {
            margin-bottom: 30px;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            min-height: 150px;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        button {
            flex: 1;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .clear-btn {
            background: #f0f0f0;
            color: #333;
        }
        
        .clear-btn:hover {
            background: #e0e0e0;
        }
        
        .results {
            display: none;
            margin-top: 30px;
            padding: 25px;
            border-radius: 15px;
            background: #f8f9fa;
        }
        
        .results.show {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .sentiment-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.3em;
            font-weight: 700;
            margin-bottom: 15px;
        }
        
        .positive {
            background: #d4edda;
            color: #155724;
        }
        
        .negative {
            background: #f8d7da;
            color: #721c24;
        }
        
        .neutral {
            background: #fff3cd;
            color: #856404;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metric {
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #333;
        }
        
        .words-section {
            margin-top: 20px;
        }
        
        .word-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .word-tag {
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .word-tag.positive {
            background: #d4edda;
            color: #155724;
        }
        
        .word-tag.negative {
            background: #f8d7da;
            color: #721c24;
        }
        
        .words-section h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-weight: 600;
            margin-top: 15px;
        }
        
        .loading.show {
            display: block;
        }
        
        .examples {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .examples h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .example-item {
            padding: 10px;
            margin: 8px 0;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .example-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Sentiment Analyzer</h1>
        <p class="subtitle">Analyze the emotional tone of any text</p>
        
        <div class="input-section">
            <textarea id="textInput" placeholder="Enter your text here... (e.g., 'I absolutely love this product! It's amazing!')"></textarea>
            <div class="button-group">
                <button class="analyze-btn" onclick="analyzeSentiment()">Analyze Sentiment</button>
                <button class="clear-btn" onclick="clearAll()">Clear</button>
            </div>
            <div class="loading" id="loading">Analyzing...</div>
        </div>
        
        <div class="results" id="results">
            <div class="sentiment-badge" id="sentimentBadge">Neutral</div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Sentiment Score</div>
                    <div class="metric-value" id="score">0.000</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Confidence</div>
                    <div class="metric-value" id="confidence">0%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Word Count</div>
                    <div class="metric-value" id="wordCount">0</div>
                </div>
            </div>
            
            <div class="words-section" id="positiveSection" style="display: none;">
                <h3>✅ Positive Indicators</h3>
                <div class="word-list" id="positiveWords"></div>
            </div>
            
            <div class="words-section" id="negativeSection" style="display: none;">
                <h3>❌ Negative Indicators</h3>
                <div class="word-list" id="negativeWords"></div>
            </div>
        </div>
        
        <div class="examples">
            <h3>📝 Try These Examples:</h3>
            <div class="example-item" onclick="useExample(this)">
                I absolutely love this product! It's amazing and works perfectly.
            </div>
            <div class="example-item" onclick="useExample(this)">
                This is the worst experience I've ever had. Totally disappointed.
            </div>
            <div class="example-item" onclick="useExample(this)">
                The weather today is okay. Nothing special.
            </div>
            <div class="example-item" onclick="useExample(this)">
                Not bad at all! Actually quite good and enjoyable.
            </div>
        </div>
    </div>
    
    <script>
        function analyzeSentiment() {
            const text = document.getElementById('textInput').value;
            
            if (!text.trim()) {
                alert('Please enter some text to analyze');
                return;
            }
            
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            
            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
                document.getElementById('loading').classList.remove('show');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during analysis');
                document.getElementById('loading').classList.remove('show');
            });
        }
        
        function displayResults(data) {
            const badge = document.getElementById('sentimentBadge');
            badge.textContent = data.label;
            badge.className = 'sentiment-badge ' + data.label.toLowerCase();
            
            document.getElementById('score').textContent = data.score.toFixed(3);
            document.getElementById('confidence').textContent = data.confidence + '%';
            document.getElementById('wordCount').textContent = data.word_count;
            
            // Display positive words
            const positiveSection = document.getElementById('positiveSection');
            const positiveWords = document.getElementById('positiveWords');
            if (data.positive_words.length > 0) {
                positiveWords.innerHTML = data.positive_words
                    .map(word => `<span class="word-tag positive">${word}</span>`)
                    .join('');
                positiveSection.style.display = 'block';
            } else {
                positiveSection.style.display = 'none';
            }
            
            // Display negative words
            const negativeSection = document.getElementById('negativeSection');
            const negativeWords = document.getElementById('negativeWords');
            if (data.negative_words.length > 0) {
                negativeWords.innerHTML = data.negative_words
                    .map(word => `<span class="word-tag negative">${word}</span>`)
                    .join('');
                negativeSection.style.display = 'block';
            } else {
                negativeSection.style.display = 'none';
            }
            
            document.getElementById('results').classList.add('show');
        }
        
        function clearAll() {
            document.getElementById('textInput').value = '';
            document.getElementById('results').classList.remove('show');
        }
        
        function useExample(element) {
            document.getElementById('textInput').value = element.textContent.trim();
            analyzeSentiment();
        }
        
        // Allow Enter key to submit
        document.getElementById('textInput').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                analyzeSentiment();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Render the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint for sentiment analysis"""
    data = request.get_json()
    text = data.get('text', '')
    
    result = analyze_sentiment(text)
    return jsonify(result)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎭 SENTIMENT ANALYSIS WEB APP")
    print("="*60)
    print("\n📍 Server starting...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5000")
    print("⌨️  Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)