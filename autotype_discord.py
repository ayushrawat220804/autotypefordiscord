import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyautogui
import time
import random
import threading
from datetime import datetime
import keyboard

class AutoTypeDiscord:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Auto Typer - 100 WPM")
        self.root.geometry("800x600")
        
        # Variables
        self.is_typing = False
        self.words_per_minute = 100
        self.delay_per_word = 60.0 / 100.0  # 0.6 seconds per word for 100 WPM
        self.words_per_line = 8  # Default 8 words per line
        self.typing_completed = False
        
        # Sample content
        self.sample_content = self.generate_sample_content()
        
        # Setup keyboard monitoring
        self.setup_keyboard_monitoring()
        
        self.setup_ui()
    
    def setup_keyboard_monitoring(self):
        """Setup keyboard monitoring for Ctrl+P to stop typing"""
        def on_ctrl_p():
            if self.is_typing:
                self.stop_typing()
        
        keyboard.add_hotkey('ctrl+p', on_ctrl_p)
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Discord Auto Typer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Words per line setting
        ttk.Label(settings_frame, text="Words per line:").grid(row=0, column=0, sticky=tk.W)
        self.words_per_line_var = tk.StringVar(value="8")
        words_spinbox = ttk.Spinbox(settings_frame, from_=6, to=10, width=10, textvariable=self.words_per_line_var)
        words_spinbox.grid(row=0, column=1, padx=(10, 0))
        
        # Content selection
        ttk.Label(settings_frame, text="Content:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.content_var = tk.StringVar(value="sample")
        content_combo = ttk.Combobox(settings_frame, textvariable=self.content_var, 
                                   values=["sample", "cross_talk", "generated_1k", "generated_10k"], state="readonly")
        content_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Start/Stop button
        self.start_button = ttk.Button(control_frame, text="Start Typing", command=self.toggle_typing)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        # Repeat button
        self.repeat_button = ttk.Button(control_frame, text="Repeat", command=self.repeat_content, state="disabled")
        self.repeat_button.grid(row=0, column=1, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready to type", foreground="green")
        self.status_label.grid(row=0, column=2, padx=(20, 0))
        
        # Content preview
        preview_frame = ttk.LabelFrame(main_frame, text="Content Preview", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.content_preview = scrolledtext.ScrolledText(preview_frame, height=15, width=80)
        self.content_preview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Instructions: Set words per line (6-10), select content, click Start Typing.\n"
                                    "Make sure Discord is open and focused before starting. Press Ctrl+P to stop.",
                               font=("Arial", 9))
        instructions.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Update preview when content changes
        content_combo.bind('<<ComboboxSelected>>', self.update_preview)
        self.update_preview()
        
    def generate_sample_content(self):
        """Generate sample content including cross-talks and 1k word paragraph"""
        
        # Sample paragraphs
        sample_paragraphs = [
            "Hello everyone! How is everyone doing today? I hope you all are having a wonderful time. The weather is really nice outside today. I was thinking about going for a walk later. Maybe I'll visit the park and enjoy some fresh air. What are your plans for the weekend?",
            
            "I love programming and learning new technologies. Python is such a versatile language that can be used for web development, data science, and automation. I've been working on some interesting projects lately. The community is so helpful and supportive.",
            
            "Music is one of my favorite things in life. It has the power to change your mood instantly. I enjoy listening to different genres from classical to electronic. Playing instruments is also very therapeutic. Do you play any instruments?",
            
            "Technology is advancing so rapidly these days. Artificial intelligence and machine learning are becoming more accessible. It's exciting to see how these technologies can help solve real-world problems. The future looks very promising indeed."
        ]
        
        # Cross-talk between two characters
        cross_talk = [
            "Alice: Hey Bob, how was your day?",
            "Bob: It was pretty good! I finished that project I was working on.",
            "Alice: That's awesome! What kind of project was it?",
            "Bob: It was a web application using React and Node.js. Took me about two weeks to complete.",
            "Alice: Wow, that sounds impressive! I've been meaning to learn React myself.",
            "Bob: You should definitely try it! It's not as hard as it seems at first.",
            "Alice: Any tips for getting started?",
            "Bob: I'd recommend starting with the official React tutorial. It's really well written.",
            "Alice: Thanks for the advice! Maybe we can work on something together sometime.",
            "Bob: That would be great! I'd love to collaborate on a project with you.",
            "Alice: Perfect! Let me know when you're free and we can brainstorm some ideas.",
            "Bob: Will do! I'm usually free on weekends if that works for you.",
            "Alice: Weekends work perfectly for me too. Looking forward to it!",
            "Bob: Same here! This is going to be fun."
        ]
        
        # Generate 1k word paragraph
        generated_1k = self.generate_1000_word_paragraph()
        
        # Generate 10k word passage
        generated_10k = self.generate_10000_word_passage()
        
        return {
            "sample": sample_paragraphs,
            "cross_talk": cross_talk,
            "generated_1k": [generated_1k],
            "generated_10k": [generated_10k]
        }
    
    def generate_1000_word_paragraph(self):
        """Generate a 1000-word paragraph"""
        topics = [
            "technology", "science", "nature", "art", "music", "literature", 
            "history", "philosophy", "travel", "food", "sports", "education"
        ]
        
        sentences = [
            "The rapid advancement of technology has fundamentally transformed the way we live, work, and communicate in the modern world.",
            "From the invention of the wheel to the development of artificial intelligence, human innovation has continuously pushed the boundaries of what is possible.",
            "Scientific discoveries have opened new frontiers in understanding the universe, from the smallest subatomic particles to the vast expanses of space.",
            "The natural world continues to amaze us with its complexity, beauty, and intricate systems that have evolved over millions of years.",
            "Art and creativity serve as essential expressions of human emotion, culture, and the human experience throughout history.",
            "Music transcends language barriers and connects people across different cultures, generations, and backgrounds.",
            "Literature preserves the wisdom, stories, and knowledge of civilizations, allowing us to learn from the past and imagine the future.",
            "History teaches us valuable lessons about human nature, societal development, and the consequences of our actions.",
            "Philosophy challenges us to question our assumptions, explore fundamental truths, and develop critical thinking skills.",
            "Travel broadens our perspectives, exposes us to new cultures, and helps us understand the diversity of human experience.",
            "Food brings people together, reflects cultural identity, and provides nourishment for both body and soul.",
            "Sports promote physical health, teamwork, discipline, and the pursuit of excellence in competitive environments.",
            "Education empowers individuals with knowledge, skills, and critical thinking abilities necessary for personal and societal growth.",
            "The digital age has revolutionized how we access information, connect with others, and conduct business on a global scale.",
            "Environmental awareness has become increasingly important as we recognize our responsibility to protect the planet for future generations.",
            "Innovation drives economic growth, creates new opportunities, and solves complex problems facing humanity.",
            "Collaboration between different fields of study often leads to breakthrough discoveries and innovative solutions.",
            "The human brain remains one of the most complex and mysterious structures in the known universe.",
            "Space exploration continues to inspire wonder and expand our understanding of the cosmos and our place within it.",
            "Renewable energy technologies offer hope for sustainable development and reducing our dependence on fossil fuels."
        ]
        
        # Generate approximately 1000 words
        paragraph = ""
        word_count = 0
        target_words = 1000
        
        while word_count < target_words:
            sentence = random.choice(sentences)
            paragraph += sentence + " "
            word_count += len(sentence.split())
            
            # Add some variety with connecting phrases
            if random.random() < 0.3 and word_count < target_words - 50:
                connectors = [
                    "Furthermore, ", "Moreover, ", "Additionally, ", "In addition, ", 
                    "However, ", "On the other hand, ", "Meanwhile, ", "Consequently, ",
                    "Therefore, ", "As a result, ", "For instance, ", "For example, "
                ]
                connector = random.choice(connectors)
                paragraph += connector
                word_count += len(connector.split())
        
        return paragraph.strip()
    
    def generate_10000_word_passage(self):
        """Generate a 10000-word comprehensive passage"""
        
        # Extended sentence templates covering various topics
        sentence_templates = [
            # Technology and Innovation
            "The digital revolution has fundamentally altered the landscape of human interaction, communication, and information exchange across all sectors of society.",
            "Artificial intelligence and machine learning technologies are rapidly evolving, creating new possibilities for automation, data analysis, and decision-making processes.",
            "Blockchain technology promises to revolutionize financial systems, supply chains, and digital identity management through decentralized and secure protocols.",
            "Quantum computing represents the next frontier in computational power, potentially solving complex problems that are currently intractable for classical computers.",
            "The Internet of Things connects billions of devices worldwide, creating smart cities, homes, and industries that respond intelligently to human needs.",
            "Cybersecurity has become increasingly critical as our dependence on digital infrastructure grows, requiring sophisticated defense mechanisms against evolving threats.",
            "Cloud computing has democratized access to powerful computing resources, enabling startups and enterprises alike to scale their operations efficiently.",
            "Virtual and augmented reality technologies are transforming entertainment, education, and professional training through immersive digital experiences.",
            "5G networks promise ultra-fast connectivity that will enable autonomous vehicles, smart cities, and real-time remote operations across vast distances.",
            "Edge computing brings processing power closer to data sources, reducing latency and enabling real-time decision-making in critical applications.",
            
            # Science and Discovery
            "Scientific research continues to push the boundaries of human knowledge, revealing the intricate mechanisms that govern our universe and biological systems.",
            "Climate science provides crucial insights into environmental changes, helping humanity understand and mitigate the impacts of global warming.",
            "Medical research advances offer hope for treating previously incurable diseases through innovative therapies, gene editing, and personalized medicine.",
            "Space exploration expands our understanding of the cosmos while inspiring technological innovations that benefit life on Earth.",
            "Neuroscience research unravels the mysteries of consciousness, memory, and cognitive processes that define human experience.",
            "Renewable energy technologies are becoming increasingly efficient and cost-effective, offering sustainable alternatives to fossil fuel dependence.",
            "Biotechnology enables the modification of living organisms for beneficial purposes, from agriculture to medicine and environmental remediation.",
            "Materials science develops new substances with extraordinary properties, enabling breakthroughs in electronics, construction, and manufacturing.",
            "Astrophysics explores the fundamental forces and structures that shape the universe, from subatomic particles to galactic superclusters.",
            "Environmental science studies the complex interactions between living organisms and their surroundings, informing conservation and sustainability efforts.",
            
            # Society and Culture
            "Cultural diversity enriches human experience by exposing individuals to different perspectives, traditions, and ways of understanding the world.",
            "Social media platforms have transformed how people connect, share information, and participate in public discourse across global communities.",
            "Education systems worldwide are adapting to prepare students for rapidly changing job markets and technological landscapes.",
            "Urbanization trends continue to reshape human settlement patterns, creating both opportunities and challenges for sustainable development.",
            "Demographic shifts influence social policies, economic systems, and cultural norms as populations age and migrate across regions.",
            "Globalization connects economies, cultures, and societies while also highlighting the importance of preserving local identities and traditions.",
            "Social movements advocate for equality, justice, and human rights, driving progressive change in institutions and societal attitudes.",
            "Mental health awareness has grown significantly, leading to better understanding and treatment of psychological conditions and emotional well-being.",
            "Workplace dynamics evolve with remote work, automation, and changing expectations about work-life balance and professional fulfillment.",
            "Community engagement strengthens social bonds and creates resilient networks that support individuals and families during challenging times.",
            
            # Philosophy and Human Nature
            "Philosophical inquiry continues to explore fundamental questions about existence, morality, knowledge, and the nature of reality itself.",
            "Ethical considerations become increasingly important as technology advances, requiring careful reflection on the implications of human innovation.",
            "Human consciousness remains one of the greatest mysteries, challenging our understanding of awareness, free will, and subjective experience.",
            "The pursuit of happiness and meaning drives human behavior, influencing personal choices and societal structures throughout history.",
            "Wisdom traditions from various cultures offer insights into living well, managing suffering, and cultivating compassion for others.",
            "Critical thinking skills enable individuals to evaluate information, make reasoned decisions, and navigate complex modern challenges.",
            "Empathy and emotional intelligence foster better relationships and create more harmonious communities across diverse populations.",
            "The human capacity for creativity and imagination drives artistic expression, scientific discovery, and innovative problem-solving.",
            "Spiritual and religious traditions provide frameworks for understanding purpose, morality, and the transcendent aspects of human experience.",
            "Personal growth and self-improvement reflect the human desire to develop potential and create positive change in individual lives.",
            
            # Economics and Development
            "Economic systems evolve to address inequality, sustainability, and the changing nature of work in the digital age.",
            "Entrepreneurship drives innovation and economic growth by creating new businesses, products, and services that meet emerging needs.",
            "Sustainable development balances economic progress with environmental protection and social equity for future generations.",
            "Financial technology innovations democratize access to banking, investment, and payment systems for underserved populations worldwide.",
            "Supply chain management becomes increasingly complex as global trade networks expand and consumer expectations rise.",
            "Consumer behavior shifts with changing values, preferences, and awareness of environmental and social impacts of purchasing decisions.",
            "Economic inequality remains a significant challenge requiring innovative policy solutions and corporate responsibility initiatives.",
            "The gig economy transforms traditional employment relationships, offering flexibility while raising questions about worker protections.",
            "International trade agreements shape global economic relationships, influencing prosperity and development across nations.",
            "Investment in human capital through education and training remains crucial for economic competitiveness and social mobility.",
            
            # Environment and Sustainability
            "Environmental conservation efforts aim to protect biodiversity, ecosystems, and natural resources for future generations.",
            "Climate change adaptation strategies help communities prepare for and respond to changing weather patterns and environmental conditions.",
            "Renewable energy adoption accelerates as costs decrease and environmental benefits become increasingly apparent.",
            "Sustainable agriculture practices balance food production with environmental protection and resource conservation.",
            "Ocean conservation addresses marine pollution, overfishing, and habitat destruction that threaten aquatic ecosystems worldwide.",
            "Forest management strategies seek to balance timber production with carbon sequestration and wildlife habitat preservation.",
            "Water resource management becomes critical as population growth and climate change stress freshwater supplies globally.",
            "Waste reduction and recycling programs minimize environmental impact while creating economic opportunities in circular economy models.",
            "Green building technologies improve energy efficiency and environmental performance in construction and urban development.",
            "Environmental education raises awareness about ecological issues and promotes sustainable lifestyle choices among diverse populations.",
            
            # Arts and Creativity
            "Artistic expression reflects human emotions, experiences, and perspectives while challenging viewers to see the world differently.",
            "Music transcends cultural boundaries, creating universal connections through rhythm, melody, and emotional resonance.",
            "Literature preserves human stories, wisdom, and imagination across generations, enriching cultural heritage and understanding.",
            "Visual arts communicate complex ideas and emotions through color, form, and composition that words cannot express.",
            "Performance arts bring stories to life through acting, dance, and theatrical presentation that engages audiences emotionally.",
            "Digital art explores new creative possibilities through technology, expanding traditional artistic boundaries and techniques.",
            "Cultural festivals celebrate diversity while fostering understanding and appreciation for different traditions and customs.",
            "Creative industries contribute significantly to economic growth while enriching society through entertainment and cultural expression.",
            "Art therapy provides healing and personal growth opportunities through creative expression and artistic engagement.",
            "Public art enhances urban environments while reflecting community values and creating shared cultural experiences.",
            
            # Health and Wellness
            "Preventive healthcare focuses on maintaining wellness and preventing disease through lifestyle choices and early intervention.",
            "Mental health support systems help individuals cope with stress, anxiety, and emotional challenges in modern life.",
            "Physical fitness and exercise contribute to overall well-being while reducing risk of chronic diseases and improving quality of life.",
            "Nutrition science guides dietary choices that support optimal health and prevent nutrition-related health problems.",
            "Sleep hygiene practices improve rest quality and support cognitive function, emotional regulation, and physical recovery.",
            "Stress management techniques help individuals maintain balance and resilience in demanding personal and professional environments.",
            "Social connections and relationships provide emotional support and contribute significantly to overall life satisfaction.",
            "Mindfulness and meditation practices promote mental clarity, emotional stability, and present-moment awareness.",
            "Healthcare accessibility remains a critical issue requiring innovative solutions to ensure quality care for all populations.",
            "Holistic approaches to wellness integrate physical, mental, emotional, and spiritual aspects of human health and well-being."
        ]
        
        # Generate approximately 10,000 words
        passage = ""
        word_count = 0
        target_words = 10000
        
        while word_count < target_words:
            sentence = random.choice(sentence_templates)
            passage += sentence + " "
            word_count += len(sentence.split())
            
            # Add connecting phrases for better flow
            if random.random() < 0.4 and word_count < target_words - 100:
                connectors = [
                    "Furthermore, ", "Moreover, ", "Additionally, ", "In addition, ", 
                    "However, ", "On the other hand, ", "Meanwhile, ", "Consequently, ",
                    "Therefore, ", "As a result, ", "For instance, ", "For example, ",
                    "Similarly, ", "Likewise, ", "In contrast, ", "Nevertheless, ",
                    "Subsequently, ", "Accordingly, ", "Specifically, ", "Particularly, ",
                    "Essentially, ", "Fundamentally, ", "Significantly, ", "Importantly, ",
                    "Notably, ", "Remarkably, ", "Interestingly, ", "Surprisingly, "
                ]
                connector = random.choice(connectors)
                passage += connector
                word_count += len(connector.split())
            
            # Add paragraph breaks for better readability
            if word_count % 200 < 10 and word_count > 200:
                passage += "\n\n"
        
        return passage.strip()
    
    def update_preview(self, event=None):
        """Update the content preview"""
        content_type = self.content_var.get()
        content = self.sample_content[content_type]
        
        self.content_preview.delete(1.0, tk.END)
        
        if content_type == "cross_talk":
            preview_text = "\n".join(content)
        else:
            preview_text = "\n\n".join(content)
        
        self.content_preview.insert(1.0, preview_text)
    
    def toggle_typing(self):
        """Start or stop typing"""
        if not self.is_typing:
            self.start_typing()
        else:
            self.stop_typing()
    
    def start_typing(self):
        """Start the typing process"""
        self.is_typing = True
        self.typing_completed = False
        self.start_button.config(text="Stop Typing")
        self.repeat_button.config(state="disabled")
        self.status_label.config(text="Typing...", foreground="red")
        
        # Start typing in a separate thread
        self.typing_thread = threading.Thread(target=self.type_content)
        self.typing_thread.daemon = True
        self.typing_thread.start()
    
    def stop_typing(self):
        """Stop the typing process"""
        self.is_typing = False
        self.start_button.config(text="Start Typing")
        self.repeat_button.config(state="normal")  # Always enable repeat button when stopped
        self.status_label.config(text="Stopped", foreground="orange")
    
    def type_content(self):
        """Type the selected content"""
        try:
            content_type = self.content_var.get()
            content = self.sample_content[content_type]
            words_per_line = int(self.words_per_line_var.get())
            
            # Give user time to focus on Discord
            self.root.after(0, lambda: self.status_label.config(text="Starting in 3 seconds...", foreground="orange"))
            time.sleep(3)
            
            if not self.is_typing:
                return
            
            self.root.after(0, lambda: self.status_label.config(text="Typing...", foreground="red"))
            
            if content_type == "cross_talk":
                # Type each line separately
                for line in content:
                    if not self.is_typing:
                        return
                    
                    # Type the line character by character for proper 100 WPM
                    self.type_text_at_100_wpm(line)
                    
                    # Brief pause before pressing enter
                    time.sleep(0.2)
                    pyautogui.press('enter')
                    
                    # Wait between lines (60 WPM = 1 second per word)
                    words_in_line = len(line.split())
                    time.sleep(words_in_line * self.delay_per_word)
            else:
                # Type paragraphs with word-per-line formatting
                for paragraph in content:
                    if not self.is_typing:
                        return
                    
                    words = paragraph.split()
                    for i in range(0, len(words), words_per_line):
                        if not self.is_typing:
                            return
                        
                        # Get words for this line
                        line_words = words[i:i + words_per_line]
                        line = " ".join(line_words)
                        
                        # Type the line character by character for proper 100 WPM
                        self.type_text_at_100_wpm(line)
                        
                        # Brief pause before pressing enter
                        time.sleep(0.2)
                        pyautogui.press('enter')
                        
                        # Wait between lines (60 WPM = 1 second per word)
                        time.sleep(len(line_words) * self.delay_per_word)
            
            # Typing completed successfully
            if self.is_typing:
                self.typing_completed = True
                self.is_typing = False
                self.root.after(0, lambda: self.status_label.config(text="Completed", foreground="green"))
                self.root.after(0, lambda: self.repeat_button.config(state="normal"))
                self.root.after(0, lambda: self.start_button.config(text="Start Typing"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.stop_typing())
    
    def type_text_at_100_wpm(self, text):
        """Type text at exactly 100 WPM (0.6 seconds per word)"""
        words = text.split()
        if not words:
            return
        
        # Calculate delay per character to achieve 100 WPM
        # 100 WPM = 100 words per minute = 0.6 seconds per word
        # Average word length is about 5 characters
        chars_per_word = 5
        delay_per_char = self.delay_per_word / chars_per_word  # ~0.12 seconds per character
        
        for char in text:
            if not self.is_typing:
                break
            pyautogui.typewrite(char)
            time.sleep(delay_per_char)
    
    def repeat_content(self):
        """Repeat the typing process"""
        if not self.is_typing:
            self.start_typing()

def main():
    root = tk.Tk()
    app = AutoTypeDiscord(root)
    
    # Handle window closing
    def on_closing():
        if app.is_typing:
            app.stop_typing()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
