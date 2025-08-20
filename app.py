import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import base64
import re
import time
from datetime import datetime

# ======================
# OPTIMIZED CONFIGURATION
# ======================
def set_background():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #333333;
                font-family: 'Arial', sans-serif;
            }
            .title {
                color: #2E86AB;
                text-align: center;
                font-size: 2.2em;
                margin-bottom: 0.3em;
                padding-top: 15px;
                font-weight: bold;
            }
            .response-box {
                background: white;
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .stButton>button {
                background: #2E86AB;
                color: white;
                border-radius: 18px;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                font-size: 0.9em;
            }
            .language-tag {
                display: inline-block;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.7em;
                margin-left: 8px;
                background: #A23B72;
                color: white;
            }
            .audio-player {
                margin-top: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# ======================
# SMART LANGUAGE DETECTION
# ======================
class SmartLanguageDetector:
    def __init__(self):
        self.english_words = {
            'what', 'where', 'when', 'why', 'how', 'which', 'who', 'is', 'are', 'am',
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'this', 'that',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'omx', 'digital', 'business', 'hours', 'contact', 'support', 'services'
        }
        
        self.hindi_romanized = {
            'kya', 'kahan', 'kab', 'kyun', 'kaise', 'kaun', 'kisne', 'kisko',
            'hai', 'hain', 'tha', 'the', 'thi', 'hum', 'tum', 'aap', 'main', 'tu',
            'mera', 'tera', 'uska', 'hamara', 'tumhara', 'aapka', 'unka',
            'omx', 'digital', 'vyapar', 'ghante', 'sampark', 'samarthan', 'sevayen'
        }
    
    def detect(self, text):
        if not text:
            return 'en'
        
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Check for Devanagari characters
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
        if has_devanagari:
            return 'hi'
        
        # Count English and Romanized Hindi words
        english_count = sum(1 for word in words if word in self.english_words)
        hindi_count = sum(1 for word in words if word in self.hindi_romanized)
        
        if english_count >= 2 and hindi_count == 0:
            return 'en'
        if hindi_count >= 2:
            return 'hi'
        
        return 'en'

# ======================
# ENHANCED FAQ ENGINE
# ======================
class EnhancedFAQEngine:
    def __init__(self):
        self.faqs = self.load_faqs()
        self.language_detector = SmartLanguageDetector()
        
    def load_faqs(self):
        return {
            "what are your business hours": "We're open from 9 AM to 6 PM, Monday to Friday.",
            "aapke vyapar ke ghante kya hain": "हम सोमवार से शुक्रवार सुबह 9 बजे से शाम 6 बजे तक खुले रहते हैं।",
            "how can i contact support": "You can reach us at support@omxdigital.com.",
            "main support se kaise sampark kar sakta hoon": "आप हमें support@omxdigital.com पर ईमेल कर सकते हैं।",
            "what services do you offer": "We provide AI-powered digital marketing, business automation, and growth solutions.",
            "aap kaun si sevayen pradaan karte hain": "हम एआई-संचालित डिजिटल मार्केटिंग, व्यवसाय स्वचालन और विकास समाधान प्रदान करते हैं।",
            "where are you located": "Our headquarters is in New Delhi, with offices in Mumbai and Bangalore.",
            "aapka office kahan hai": "हमारा मुख्यालय नई दिल्ली में है, और मुंबई और बैंगलोर में कार्यालय हैं।",
            "what is omx digital": "OMX Digital is an AI-powered platform that helps businesses automate and optimize their operations.",
            "omx digital kya hai": "OMX Digital एक एआई-संचालित प्लेटफॉर्म है जो व्यवसायों को उनके संचालन को स्वचालित और अनुकूलित करने में मदद करता है।",
            "how does it work": "Our platform uses advanced AI algorithms to analyze your business processes and provide automated solutions.",
            "yah kaise kaam karta hai": "हमारा प्लेटफॉर्म उन्नत एआई एल्गोरिदम का उपयोग करता है जो आपके व्यावसायिक प्रक्रियाओं का विश्लेषण करता है और स्वचालित समाधान प्रदान करता है。",
            "what is your pricing": "We offer flexible pricing plans based on your business needs. Contact us for details.",
            "aapki keemat kya hai": "हम आपकी व्यावसायिक आवश्यकताओं के आधार पर लचीले मूल्य निर्धारण योजनाएं प्रदान करते हैं। विवरण के लिए हमसे संपर्क करें。",
            "do you offer demos": "Yes, we offer free demos to show how our platform can help your business.",
            "kya aap demo pradaan karte hain": "हाँ, हम मुफ्त डेमो प्रदान करते हैं जो दिखाते हैं कि हमारा प्लेटफॉर्म आपके व्यवसाय में कैसे मदद कर सकता है。"
        }
    
    def _clean_text(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def find_best_match(self, user_question):
        if not user_question:
            return None
            
        clean_q = self._clean_text(user_question)
        
        best_match = None
        best_score = 0
        
        for question in self.faqs.keys():
            clean_question = self._clean_text(question)
            score = self._calculate_similarity(clean_q, clean_question)
            if score > best_score:
                best_score = score
                best_match = question
        
        return best_match if best_score > 0.4 else None
    
    def _calculate_similarity(self, text1, text2):
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        common = words1.intersection(words2)
        return len(common) / max(len(words1), len(words2))

# ======================
# BALANCED VOICE PROCESSOR
# ======================
class BalancedVoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 350
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.7
        self.recognizer.phrase_time_limit = 4
    
    def recognize_speech(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                st.info("🎤 Speak now... (English or Hindi)")
                
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)
                
                english_text = self._try_english(audio)
                hindi_text = self._try_hindi(audio)
                
                if english_text and hindi_text:
                    if len(english_text.split()) >= len(hindi_text.split()):
                        return english_text, 'en'
                    else:
                        return hindi_text, 'hi'
                elif english_text:
                    return english_text, 'en'
                elif hindi_text:
                    return hindi_text, 'hi'
                else:
                    return None, None
                        
        except sr.WaitTimeoutError:
            st.warning("Please speak louder or closer to the microphone")
        except Exception as e:
            st.error(f"Microphone error: {str(e)}")
        
        return None, None
    
    def _try_english(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language='en-US')
            return text if text and len(text.strip()) > 1 else None
        except:
            return None
    
    def _try_hindi(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language='hi-IN')
            return text if text and len(text.strip()) > 1 else None
        except:
            return None

# ======================
# FIXED SPEECH PROCESSING
# ======================
def text_to_speech(text, lang):
    """Reliable text-to-speech conversion"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = f"response_{int(time.time() * 1000)}.mp3"  # Unique filename with milliseconds
        tts.save(filename)
        return filename
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

def display_audio_player(file_path):
    """Display audio player with reliable playback"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_bytes).decode()
            
            # Create audio HTML with controls and autoplay
            audio_html = f"""
            <div class="audio-player">
                <audio controls autoplay style="width: 100%">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """
            
            # Display the audio player
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # Clean up the file after display
            time.sleep(2)  # Wait a bit before cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
    except Exception as e:
        st.error(f"Audio playback error: {e}")
    return False

# ======================
# MAIN APPLICATION
# ======================
def main():
    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'last_question_time' not in st.session_state:
        st.session_state.last_question_time = 0
    
    set_background()
    
    faq_engine = EnhancedFAQEngine()
    voice_processor = BalancedVoiceProcessor()
    
    st.title("⚡ OMX Digital Voice Assistant")
    
    # Input section
    st.subheader("Ask Your Question")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 Start Recording", use_container_width=True, key="voice_btn"):
            if not st.session_state.processing:
                st.session_state.processing = True
                with st.spinner("Listening..."):
                    question, lang = voice_processor.recognize_speech()
                    if question:
                        st.success(f"Detected: {'Hindi' if lang == 'hi' else 'English'}")
                        process_question(question, lang, faq_engine)
                    else:
                        st.error("Could not recognize speech. Please try again.")
                st.session_state.processing = False
    
    with col2:
        question = st.text_input("Or type your question:", key="text_input")
        if st.button("📝 Submit Text", use_container_width=True, key="text_btn") and question:
            if not st.session_state.processing:
                st.session_state.processing = True
                lang = faq_engine.language_detector.detect(question)
                process_question(question, lang, faq_engine)
                st.session_state.processing = False
    
    # Display conversation
    st.subheader("Conversation History")
    if not st.session_state.conversation:
        st.info("No conversation yet. Ask a question using voice or text!")
    
    for i, (speaker, text, lang, audio_file) in enumerate(st.session_state.conversation):
        lang_tag = "🇮🇳 Hindi" if lang == 'hi' else "🇬🇧 English"
        st.markdown(f"""
        <div class="response-box">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong>{speaker}:</strong>
                <span class="language-tag">{lang_tag}</span>
            </div>
            <div style="margin-top: 8px;">{text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show audio player for the latest assistant response
        if speaker == "Assistant" and i == len(st.session_state.conversation) - 1 and audio_file:
            if os.path.exists(audio_file):
                display_audio_player(audio_file)
    
    # Quick questions
    st.subheader("Try These Questions:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**In English:**")
        en_questions = ["what is omx digital", "what are your business hours", "how can i contact support"]
        for q in en_questions:
            if st.button(f"❓ {q}", key=f"en_{q}"):
                if not st.session_state.processing:
                    process_question(q, 'en', faq_engine)
    
    with col2:
        st.write("**In Hindi:**")
        hi_questions = ["omx digital kya hai", "aapke vyapar ke ghante kya hain", "main support se kaise sampark kar sakta hoon"]
        for q in hi_questions:
            if st.button(f"❓ {q}", key=f"hi_{q}"):
                if not st.session_state.processing:
                    process_question(q, 'hi', faq_engine)

def process_question(question, lang, faq_engine):
    """Process the question and generate response"""
    current_time = time.time()
    
    # Prevent processing the same question multiple times in quick succession
    if current_time - st.session_state.last_question_time < 1.0:
        return
    
    st.session_state.last_question_time = current_time
    
    # Add to conversation
    st.session_state.conversation.append(("You", question, lang, None))
    
    # Find match
    matched_q = faq_engine.find_best_match(question)
    
    if matched_q:
        answer = faq_engine.faqs[matched_q]
        answer_lang = faq_engine.language_detector.detect(answer)
        
        # Generate speech first
        audio_file = text_to_speech(answer, answer_lang)
        
        # Add to conversation with audio file reference
        st.session_state.conversation.append(("Assistant", answer, answer_lang, audio_file))
    else:
        if lang == 'hi':
            no_answer = "माफ कीजिए, मुझे इस प्रश्न का उत्तर नहीं पता। कृपया कोई अन्य प्रश्न पूछें।"
        else:
            no_answer = "Sorry, I don't know the answer to this question. Please ask something else."
        
        # Generate speech
        audio_file = text_to_speech(no_answer, lang)
        
        # Add to conversation with audio file reference
        st.session_state.conversation.append(("Assistant", no_answer, lang, audio_file))
    
    # Limit conversation history
    if len(st.session_state.conversation) > 10:
        st.session_state.conversation = st.session_state.conversation[-10:]

if __name__ == "__main__":
    main()