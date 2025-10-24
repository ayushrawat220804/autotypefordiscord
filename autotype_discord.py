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
                                   values=["sample", "cross_talk", "generated_1k", "generated_10k", "generated_25k"], state="readonly")
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
        
        # Generate 25k word passage
        generated_25k = self.generate_25000_word_passage()
        
        return {
            "sample": sample_paragraphs,
            "cross_talk": cross_talk,
            "generated_1k": [generated_1k],
            "generated_10k": [generated_10k],
            "generated_25k": [generated_25k]
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
    
    def generate_25000_word_passage(self):
        """Generate a comprehensive 25000-word passage covering diverse topics"""
        
        # Extensive sentence templates covering a wide range of topics
        sentence_templates = [
            # Technology, AI, and Digital Transformation
            "The digital revolution has fundamentally altered the landscape of human interaction, communication, and information exchange across all sectors of society in profound and unprecedented ways.",
            "Artificial intelligence and machine learning technologies are rapidly evolving, creating new possibilities for automation, data analysis, and decision-making processes that were once thought impossible.",
            "Blockchain technology promises to revolutionize financial systems, supply chains, and digital identity management through decentralized and secure protocols that ensure transparency.",
            "Quantum computing represents the next frontier in computational power, potentially solving complex problems that are currently intractable for classical computers and opening new scientific horizons.",
            "The Internet of Things connects billions of devices worldwide, creating smart cities, homes, and industries that respond intelligently to human needs and environmental conditions.",
            "Cybersecurity has become increasingly critical as our dependence on digital infrastructure grows, requiring sophisticated defense mechanisms against evolving threats and cyber attacks.",
            "Cloud computing has democratized access to powerful computing resources, enabling startups and enterprises alike to scale their operations efficiently and cost-effectively.",
            "Virtual and augmented reality technologies are transforming entertainment, education, and professional training through immersive digital experiences that blur the line between physical and virtual worlds.",
            "5G networks promise ultra-fast connectivity that will enable autonomous vehicles, smart cities, and real-time remote operations across vast distances with minimal latency.",
            "Edge computing brings processing power closer to data sources, reducing latency and enabling real-time decision-making in critical applications such as autonomous vehicles and industrial automation.",
            "Machine learning algorithms are becoming increasingly sophisticated, enabling computers to recognize patterns, make predictions, and learn from experience without explicit programming.",
            "Data analytics tools help organizations extract valuable insights from massive datasets, driving informed decision-making and strategic planning across various industries.",
            "Automation technologies are transforming manufacturing, logistics, and service industries by increasing efficiency, reducing costs, and improving quality while raising questions about workforce adaptation.",
            "Natural language processing enables computers to understand and generate human language, powering virtual assistants, translation services, and content generation systems.",
            "Computer vision technology allows machines to interpret and analyze visual information from the world, enabling applications from facial recognition to autonomous navigation.",
            "Robotics combines mechanical engineering, electronics, and artificial intelligence to create machines that can perform complex tasks in manufacturing, healthcare, and exploration.",
            "Software development methodologies continue to evolve, with agile practices and DevOps approaches enabling faster iteration and more reliable deployment of applications.",
            "Open source software fosters collaboration and innovation by allowing developers worldwide to contribute to and improve upon shared codebases and tools.",
            "Mobile computing has transformed how people access information and services, with smartphones becoming essential tools for communication, commerce, and entertainment.",
            "Digital transformation initiatives help traditional businesses adapt to the digital age by integrating technology into all aspects of their operations and customer interactions.",
            
            # Science, Research, and Discovery
            "Scientific research continues to push the boundaries of human knowledge, revealing the intricate mechanisms that govern our universe and biological systems through rigorous experimentation.",
            "Climate science provides crucial insights into environmental changes, helping humanity understand and mitigate the impacts of global warming through comprehensive data analysis.",
            "Medical research advances offer hope for treating previously incurable diseases through innovative therapies, gene editing, and personalized medicine approaches.",
            "Space exploration expands our understanding of the cosmos while inspiring technological innovations that benefit life on Earth and prepare humanity for future interplanetary missions.",
            "Neuroscience research unravels the mysteries of consciousness, memory, and cognitive processes that define human experience and inform treatments for neurological disorders.",
            "Renewable energy technologies are becoming increasingly efficient and cost-effective, offering sustainable alternatives to fossil fuel dependence and reducing carbon emissions.",
            "Biotechnology enables the modification of living organisms for beneficial purposes, from agriculture to medicine and environmental remediation, raising ethical considerations.",
            "Materials science develops new substances with extraordinary properties, enabling breakthroughs in electronics, construction, and manufacturing that improve quality of life.",
            "Astrophysics explores the fundamental forces and structures that shape the universe, from subatomic particles to galactic superclusters and dark matter phenomena.",
            "Environmental science studies the complex interactions between living organisms and their surroundings, informing conservation and sustainability efforts worldwide.",
            "Genetics research reveals the blueprint of life encoded in DNA, enabling advances in personalized medicine, agriculture, and our understanding of evolution.",
            "Chemistry investigates the properties and transformations of matter, leading to the development of new materials, pharmaceuticals, and sustainable technologies.",
            "Physics explores the fundamental laws governing the universe, from quantum mechanics to relativity theory, providing the foundation for technological innovation.",
            "Oceanography studies the world's oceans, revealing ecosystems, currents, and geological features that influence global climate and support diverse marine life.",
            "Meteorology advances our ability to predict weather patterns and understand atmospheric phenomena, helping communities prepare for severe weather events.",
            "Geology examines Earth's structure, composition, and processes, informing resource extraction, hazard prediction, and our understanding of planetary formation.",
            "Ecology investigates the relationships between organisms and their environments, guiding conservation efforts and ecosystem management strategies.",
            "Astronomy observes celestial objects and phenomena, expanding our knowledge of the universe's origin, evolution, and the potential for extraterrestrial life.",
            "Biochemistry bridges biology and chemistry, studying the chemical processes within living organisms that sustain life and enable biological functions.",
            "Molecular biology examines biological processes at the molecular level, revealing how genetic information is stored, expressed, and regulated in living cells.",
            
            # Society, Culture, and Human Development
            "Cultural diversity enriches human experience by exposing individuals to different perspectives, traditions, and ways of understanding the world around us.",
            "Social media platforms have transformed how people connect, share information, and participate in public discourse across global communities both positively and negatively.",
            "Education systems worldwide are adapting to prepare students for rapidly changing job markets and technological landscapes through innovative teaching methods.",
            "Urbanization trends continue to reshape human settlement patterns, creating both opportunities and challenges for sustainable development and quality of life.",
            "Demographic shifts influence social policies, economic systems, and cultural norms as populations age and migrate across regions seeking better opportunities.",
            "Globalization connects economies, cultures, and societies while also highlighting the importance of preserving local identities and traditions in an interconnected world.",
            "Social movements advocate for equality, justice, and human rights, driving progressive change in institutions and societal attitudes through collective action.",
            "Mental health awareness has grown significantly, leading to better understanding and treatment of psychological conditions and emotional well-being across populations.",
            "Workplace dynamics evolve with remote work, automation, and changing expectations about work-life balance and professional fulfillment in modern careers.",
            "Community engagement strengthens social bonds and creates resilient networks that support individuals and families during challenging times and crisis situations.",
            "Language diversity preserves cultural heritage while presenting challenges and opportunities for communication in increasingly multicultural societies worldwide.",
            "Religious and spiritual traditions provide meaning, moral guidance, and community for billions of people across different cultures and geographical regions.",
            "Family structures vary across cultures and evolve over time, reflecting changing social norms, economic conditions, and individual choices about relationships.",
            "Gender equality movements challenge traditional roles and discrimination, promoting equal opportunities and rights for people of all gender identities.",
            "Youth culture influences fashion, music, and social trends while younger generations navigate the challenges of growing up in rapidly changing societies.",
            "Aging populations require adaptations in healthcare, social services, and economic systems to support older adults' quality of life and dignity.",
            "Immigration shapes societies by bringing diverse perspectives, skills, and cultural practices while raising questions about integration and national identity.",
            "Civil society organizations play crucial roles in advocating for public interests, providing services, and holding governments and corporations accountable.",
            "Human rights frameworks establish universal standards for dignity, freedom, and justice, though implementation varies widely across nations and contexts.",
            "Social cohesion depends on shared values, mutual respect, and institutions that promote cooperation and resolve conflicts peacefully within diverse communities.",
            
            # Philosophy, Ethics, and Human Nature
            "Philosophical inquiry continues to explore fundamental questions about existence, morality, knowledge, and the nature of reality itself through reasoned argument.",
            "Ethical considerations become increasingly important as technology advances, requiring careful reflection on the implications of human innovation and scientific progress.",
            "Human consciousness remains one of the greatest mysteries, challenging our understanding of awareness, free will, and subjective experience in profound ways.",
            "The pursuit of happiness and meaning drives human behavior, influencing personal choices and societal structures throughout history and across cultures.",
            "Wisdom traditions from various cultures offer insights into living well, managing suffering, and cultivating compassion for others through time-tested practices.",
            "Critical thinking skills enable individuals to evaluate information, make reasoned decisions, and navigate complex modern challenges with clarity and purpose.",
            "Empathy and emotional intelligence foster better relationships and create more harmonious communities across diverse populations by promoting understanding.",
            "The human capacity for creativity and imagination drives artistic expression, scientific discovery, and innovative problem-solving in all domains of life.",
            "Spiritual and religious traditions provide frameworks for understanding purpose, morality, and the transcendent aspects of human experience throughout history.",
            "Personal growth and self-improvement reflect the human desire to develop potential and create positive change in individual lives through continuous learning.",
            "Moral philosophy examines questions of right and wrong, virtue and vice, providing frameworks for ethical decision-making in personal and public life.",
            "Epistemology investigates the nature and limits of knowledge, helping us understand how we know what we know and the foundations of justified belief.",
            "Aesthetics explores the nature of beauty, art, and taste, examining how humans perceive and create aesthetic experiences across different mediums.",
            "Logic provides tools for valid reasoning and argumentation, enabling clear thinking and effective communication of complex ideas and positions.",
            "Political philosophy examines questions of justice, authority, and the ideal organization of society, influencing governance systems and public policy.",
            "Existentialism emphasizes individual freedom, responsibility, and the creation of meaning in an apparently meaningless universe through authentic choices.",
            "Metaphysics investigates the fundamental nature of reality, including questions about causation, time, space, and the relationship between mind and matter.",
            "Philosophy of mind explores consciousness, cognition, and the relationship between mental states and brain processes in humans and potentially other beings.",
            "Ethics of care emphasizes relationships, interdependence, and contextual moral reasoning as alternatives to abstract principles in ethical decision-making.",
            "Pragmatism focuses on practical consequences and real-world applications of ideas, valuing knowledge that proves useful in solving concrete problems.",
            
            # Economics, Business, and Development
            "Economic systems evolve to address inequality, sustainability, and the changing nature of work in the digital age through policy innovation.",
            "Entrepreneurship drives innovation and economic growth by creating new businesses, products, and services that meet emerging needs and market demands.",
            "Sustainable development balances economic progress with environmental protection and social equity for future generations through integrated planning.",
            "Financial technology innovations democratize access to banking, investment, and payment systems for underserved populations worldwide through mobile platforms.",
            "Supply chain management becomes increasingly complex as global trade networks expand and consumer expectations rise for faster delivery and transparency.",
            "Consumer behavior shifts with changing values, preferences, and awareness of environmental and social impacts of purchasing decisions in modern markets.",
            "Economic inequality remains a significant challenge requiring innovative policy solutions and corporate responsibility initiatives to ensure shared prosperity.",
            "The gig economy transforms traditional employment relationships, offering flexibility while raising questions about worker protections and benefits.",
            "International trade agreements shape global economic relationships, influencing prosperity and development across nations through tariff and regulatory policies.",
            "Investment in human capital through education and training remains crucial for economic competitiveness and social mobility in knowledge economies.",
            "Microfinance initiatives provide small loans to entrepreneurs in developing countries, enabling economic empowerment and poverty reduction through entrepreneurship.",
            "Corporate social responsibility encourages businesses to consider their impacts on society and environment beyond profit maximization and shareholder value.",
            "Circular economy models aim to minimize waste and maximize resource efficiency by designing products for reuse, repair, and recycling.",
            "Innovation ecosystems bring together entrepreneurs, investors, researchers, and support organizations to foster technological advancement and economic growth.",
            "Labor markets adapt to technological change, with some jobs disappearing while new opportunities emerge requiring different skills and competencies.",
            "Trade policy balances domestic interests with international cooperation, affecting industries, workers, and consumers through tariffs and regulations.",
            "Monetary policy influences economic activity through interest rates and money supply, affecting inflation, employment, and overall economic stability.",
            "Fiscal policy uses government spending and taxation to influence economic conditions and achieve policy objectives like full employment and stable prices.",
            "Market efficiency theory suggests that prices reflect all available information, though behavioral economics reveals systematic deviations from rational behavior.",
            "Economic development strategies vary across countries, reflecting different priorities, resources, and political systems in pursuing prosperity and well-being.",
            
            # Environment, Sustainability, and Conservation
            "Environmental conservation efforts aim to protect biodiversity, ecosystems, and natural resources for future generations through habitat preservation and restoration.",
            "Climate change adaptation strategies help communities prepare for and respond to changing weather patterns and environmental conditions through resilient infrastructure.",
            "Renewable energy adoption accelerates as costs decrease and environmental benefits become increasingly apparent, driving transition from fossil fuels.",
            "Sustainable agriculture practices balance food production with environmental protection and resource conservation through organic farming and precision agriculture.",
            "Ocean conservation addresses marine pollution, overfishing, and habitat destruction that threaten aquatic ecosystems worldwide and the communities depending on them.",
            "Forest management strategies seek to balance timber production with carbon sequestration and wildlife habitat preservation in increasingly threatened ecosystems.",
            "Water resource management becomes critical as population growth and climate change stress freshwater supplies globally, requiring efficient use and conservation.",
            "Waste reduction and recycling programs minimize environmental impact while creating economic opportunities in circular economy models that value resources.",
            "Green building technologies improve energy efficiency and environmental performance in construction and urban development through innovative materials and designs.",
            "Environmental education raises awareness about ecological issues and promotes sustainable lifestyle choices among diverse populations through formal and informal learning.",
            "Biodiversity conservation protects the variety of life on Earth, recognizing that species diversity strengthens ecosystems and provides essential services to humanity.",
            "Pollution control regulations limit emissions and discharges that harm air, water, and soil quality, protecting public health and environmental integrity.",
            "Ecosystem services provide essential benefits like clean air, water filtration, and climate regulation that support human well-being and economic activities.",
            "Wildlife protection efforts combat poaching, habitat loss, and human-wildlife conflict through law enforcement, community engagement, and habitat corridors.",
            "Sustainable fishing practices aim to maintain fish populations at healthy levels while supporting the livelihoods of fishing communities worldwide.",
            "Reforestation and afforestation projects restore degraded lands and create new forests that sequester carbon and provide habitat for wildlife.",
            "Green energy infrastructure includes solar panels, wind turbines, and hydroelectric systems that generate electricity without fossil fuel combustion.",
            "Environmental impact assessments evaluate potential consequences of development projects, informing decisions that balance economic and environmental considerations.",
            "Climate mitigation strategies reduce greenhouse gas emissions through energy efficiency, renewable energy, and changes in land use and industrial processes.",
            "Sustainable tourism promotes travel practices that minimize environmental impact while benefiting local communities and supporting conservation efforts.",
            
            # Arts, Creativity, and Cultural Expression
            "Artistic expression reflects human emotions, experiences, and perspectives while challenging viewers to see the world differently through creative mediums.",
            "Music transcends cultural boundaries, creating universal connections through rhythm, melody, and emotional resonance that speaks to the human condition.",
            "Literature preserves human stories, wisdom, and imagination across generations, enriching cultural heritage and understanding through written narratives.",
            "Visual arts communicate complex ideas and emotions through color, form, and composition that words cannot express, engaging viewers viscerally.",
            "Performance arts bring stories to life through acting, dance, and theatrical presentation that engages audiences emotionally and intellectually.",
            "Digital art explores new creative possibilities through technology, expanding traditional artistic boundaries and techniques in innovative directions.",
            "Cultural festivals celebrate diversity while fostering understanding and appreciation for different traditions and customs through shared experiences.",
            "Creative industries contribute significantly to economic growth while enriching society through entertainment and cultural expression in various forms.",
            "Art therapy provides healing and personal growth opportunities through creative expression and artistic engagement for individuals facing challenges.",
            "Public art enhances urban environments while reflecting community values and creating shared cultural experiences accessible to all residents.",
            "Film and cinema combine visual storytelling, performance, and technical artistry to create immersive narratives that influence culture and society.",
            "Photography captures moments in time, documenting history, revealing beauty, and providing evidence while serving as powerful artistic expression.",
            "Architecture shapes the built environment, combining functional design with aesthetic vision to create spaces that inspire and serve human needs.",
            "Fashion design expresses personal and cultural identity while pushing creative boundaries in textiles, form, and wearable art throughout history.",
            "Sculpture transforms materials into three-dimensional forms that occupy space and invite interaction, from ancient monuments to contemporary installations.",
            "Craftsmanship preserves traditional skills and techniques while adapting to contemporary needs, creating objects of beauty and utility by hand.",
            "Poetry distills language into concentrated expressions of emotion, experience, and insight through carefully chosen words and rhythmic structures.",
            "Theater brings communities together to experience live performance, creating shared moments that cannot be replicated through recorded media.",
            "Street art democratizes artistic expression by bringing creativity to public spaces, often conveying social messages and challenging conventions.",
            "Cultural heritage preservation protects historical artifacts, sites, and traditions that connect present generations to their past and inform future identity.",
            
            # Health, Medicine, and Well-being
            "Preventive healthcare focuses on maintaining wellness and preventing disease through lifestyle choices and early intervention before conditions become serious.",
            "Mental health support systems help individuals cope with stress, anxiety, and emotional challenges in modern life through therapy and community resources.",
            "Physical fitness and exercise contribute to overall well-being while reducing risk of chronic diseases and improving quality of life across all ages.",
            "Nutrition science guides dietary choices that support optimal health and prevent nutrition-related health problems through evidence-based recommendations.",
            "Sleep hygiene practices improve rest quality and support cognitive function, emotional regulation, and physical recovery through consistent routines.",
            "Stress management techniques help individuals maintain balance and resilience in demanding personal and professional environments through various strategies.",
            "Social connections and relationships provide emotional support and contribute significantly to overall life satisfaction and longevity through meaningful bonds.",
            "Mindfulness and meditation practices promote mental clarity, emotional stability, and present-moment awareness through regular contemplative exercises.",
            "Healthcare accessibility remains a critical issue requiring innovative solutions to ensure quality care for all populations regardless of income or location.",
            "Holistic approaches to wellness integrate physical, mental, emotional, and spiritual aspects of human health and well-being for comprehensive care.",
            "Public health initiatives prevent disease and promote health at population level through vaccination programs, health education, and policy interventions.",
            "Telemedicine expands healthcare access through remote consultations, enabling patients to receive care regardless of geographical barriers or mobility limitations.",
            "Precision medicine tailors treatment to individual characteristics, including genetic profiles, enabling more effective and personalized healthcare interventions.",
            "Health literacy empowers individuals to understand health information and make informed decisions about their care through education and clear communication.",
            "Addiction treatment combines medical intervention, counseling, and social support to help individuals overcome substance dependence and rebuild their lives.",
            "Pain management addresses acute and chronic pain through multimodal approaches including medication, physical therapy, and psychological interventions.",
            "Rehabilitation services help individuals recover function and independence after injury, illness, or surgery through targeted therapeutic interventions.",
            "Immunology research advances our understanding of the immune system, leading to better vaccines, treatments for autoimmune diseases, and cancer therapies.",
            "Epidemiology studies disease patterns in populations, identifying risk factors and informing public health strategies to prevent and control outbreaks.",
            "Palliative care improves quality of life for patients with serious illnesses by addressing physical symptoms, emotional needs, and spiritual concerns.",
            
            # Education, Learning, and Knowledge
            "Educational innovation transforms teaching and learning through technology, active learning strategies, and student-centered approaches that engage learners.",
            "Lifelong learning becomes essential as rapid change requires continuous skill development and knowledge acquisition throughout one's career and life.",
            "Digital literacy enables individuals to effectively navigate, evaluate, and create information using digital technologies in personal and professional contexts.",
            "Higher education prepares students for careers and citizenship while advancing knowledge through research and critical inquiry across disciplines.",
            "Early childhood education provides foundational experiences that shape cognitive, social, and emotional development during critical formative years.",
            "Vocational training develops practical skills for specific careers, offering alternatives to traditional academic pathways and meeting industry workforce needs.",
            "Online learning expands educational access, enabling students to learn anytime and anywhere through internet-connected devices and platforms.",
            "Special education adapts instruction to meet diverse learning needs, ensuring students with disabilities receive appropriate support and accommodations.",
            "Curriculum development balances core knowledge, practical skills, and values education to prepare students for success in complex modern societies.",
            "Assessment practices measure learning outcomes and provide feedback to students and teachers, informing instructional improvements and accountability.",
            "Educational equity ensures all students have access to quality learning opportunities regardless of background, income, or circumstances through targeted support.",
            "STEM education emphasizes science, technology, engineering, and mathematics to prepare students for careers in high-demand technical fields.",
            "Liberal arts education develops critical thinking, communication, and analytical skills applicable across diverse careers and life situations.",
            "Bilingual education preserves heritage languages while developing proficiency in additional languages, offering cognitive and cultural benefits.",
            "Project-based learning engages students in authentic tasks that develop problem-solving skills and deeper understanding through hands-on experience.",
            "Teacher professional development improves instructional quality through ongoing training, collaboration, and reflection on teaching practices.",
            "Educational psychology applies psychological principles to understand how students learn and develop, informing more effective teaching strategies.",
            "Informal education occurs outside traditional classrooms through museums, libraries, and community programs that promote learning throughout life.",
            "Academic research advances human knowledge through systematic investigation, contributing to understanding across all fields of inquiry.",
            "Study skills and metacognition help students learn more effectively by understanding their own learning processes and using appropriate strategies.",
            
            # History, Heritage, and Collective Memory
            "Historical understanding provides perspective on current events by revealing patterns, causes, and consequences of past human actions and decisions.",
            "Archaeological discoveries unearth material remains of past civilizations, offering tangible evidence of how ancient peoples lived and organized societies.",
            "Oral histories preserve personal narratives and community memories that might otherwise be lost, capturing diverse perspectives on historical events.",
            "Historical preservation protects buildings, sites, and artifacts that embody cultural heritage and connect communities to their past identities.",
            "Historiography examines how history is written and interpreted, revealing biases and perspectives that shape our understanding of the past.",
            "Ancient civilizations developed complex societies, technologies, and cultural achievements that continue to influence modern life in numerous ways.",
            "Colonial legacies continue to shape political, economic, and social relationships between nations and within formerly colonized societies.",
            "Industrial revolutions transformed economies, societies, and daily life through mechanization, urbanization, and new forms of social organization.",
            "World wars reshaped global politics and society in the twentieth century, leading to international institutions and changed power dynamics.",
            "Social history examines everyday lives of ordinary people rather than just political leaders, revealing diverse experiences across time periods.",
            "Cultural memory shapes collective identity and values through shared stories, symbols, and commemorations that bind communities together.",
            "Historical revisionism challenges established narratives by incorporating new evidence and perspectives, leading to more nuanced understandings.",
            "Primary sources provide direct evidence from historical periods, enabling researchers to interpret past events without intermediary accounts.",
            "Comparative history examines similarities and differences across societies and time periods, revealing general patterns and unique circumstances.",
            "Historical methodology applies rigorous techniques to evaluate sources, construct arguments, and draw conclusions about past events and conditions.",
            "Public history makes historical knowledge accessible and relevant to general audiences through museums, documentaries, and community engagement.",
            "Digital humanities apply computational methods to historical research, enabling analysis of large datasets and new forms of scholarly communication.",
            "Historical trauma affects communities that have experienced collective violence or oppression, influencing present-day social and psychological conditions.",
            "Commemoration practices honor significant events and individuals through monuments, holidays, and rituals that reinforce collective memory and values.",
            "Historical consciousness involves awareness of how past shapes present and influences how individuals and societies understand their place in time.",
            
            # Psychology, Behavior, and Human Development
            "Cognitive psychology studies mental processes including perception, memory, reasoning, and problem-solving that underlie human thought and behavior.",
            "Developmental psychology examines how people grow and change throughout the lifespan from infancy through old age across multiple domains.",
            "Social psychology investigates how individuals think, feel, and behave in social contexts, revealing powerful influences of situations on actions.",
            "Personality psychology explores individual differences in characteristic patterns of thinking, feeling, and behaving that remain relatively stable over time.",
            "Clinical psychology applies psychological science to assess and treat mental health disorders through evidence-based therapeutic interventions.",
            "Behavioral economics reveals systematic ways that human decision-making deviates from rational models due to cognitive biases and heuristics.",
            "Positive psychology focuses on human strengths, well-being, and flourishing rather than only studying dysfunction and pathology.",
            "Neuropsychology examines relationships between brain function and behavior, informing understanding of cognitive processes and clinical conditions.",
            "Motivation theory explores factors that initiate, direct, and sustain goal-directed behaviors across different contexts and individuals.",
            "Learning theory describes how organisms acquire new behaviors and knowledge through experience, conditioning, and observational learning.",
            "Emotional intelligence involves recognizing, understanding, and managing emotions in oneself and others, contributing to personal and social success.",
            "Attachment theory explains how early relationships with caregivers shape patterns of relating to others throughout life in profound ways.",
            "Resilience research identifies factors that help individuals adapt and thrive despite adversity, trauma, or significant stress.",
            "Group dynamics examines how people interact within teams and organizations, influencing cooperation, conflict, and collective performance.",
            "Perception involves organizing and interpreting sensory information to create meaningful experiences of the world around us.",
            "Memory processes encode, store, and retrieve information, enabling learning and the continuity of personal identity over time.",
            "Decision-making research reveals strategies and biases that influence choices under uncertainty and in complex situations.",
            "Habit formation explains how behaviors become automatic through repetition, offering insights for behavior change and self-improvement.",
            "Self-concept encompasses beliefs and feelings about oneself that influence motivation, behavior, and emotional responses to life events.",
            "Conformity and obedience research demonstrates how social influence shapes individual behavior in ways that sometimes contradict personal values.",
            
            # Communication, Media, and Information
            "Effective communication involves clearly expressing ideas and actively listening to others in ways that build understanding and connection.",
            "Mass media influences public opinion, cultural norms, and political processes through news coverage, entertainment, and advertising content.",
            "Digital media literacy enables critical evaluation of online information, recognition of misinformation, and responsible digital citizenship.",
            "Interpersonal communication builds relationships through verbal and nonverbal exchanges that convey meaning, emotion, and social connection.",
            "Journalism serves democracy by investigating issues, reporting facts, and holding power accountable through independent professional standards.",
            "Public relations manages communication between organizations and publics to build reputation and navigate complex stakeholder relationships.",
            "Advertising uses persuasive communication to influence consumer behavior and brand perceptions through creative messages across media platforms.",
            "Information architecture organizes and structures content to make it findable and usable in digital environments and physical spaces.",
            "Visual communication conveys ideas through images, graphics, and design elements that complement or replace written text effectively.",
            "Cross-cultural communication navigates differences in norms, values, and communication styles across cultural contexts to build mutual understanding.",
            "Rhetoric studies persuasive communication through analysis of arguments, appeals, and stylistic techniques used to influence audiences.",
            "Media production involves creative and technical processes of creating content for various platforms including film, television, and digital media.",
            "Information systems manage data collection, storage, processing, and distribution to support organizational decision-making and operations.",
            "Organizational communication facilitates coordination, builds culture, and enables effective functioning within businesses and institutions.",
            "Political communication shapes public discourse through campaigns, debates, and strategic messaging that influence electoral and policy outcomes.",
            "Broadcasting distributes audio and video content to wide audiences through traditional and digital channels for information and entertainment.",
            "Network society describes contemporary social organization characterized by interconnected individuals and groups enabled by communication technologies.",
            "Information overload challenges individuals to filter and prioritize vast amounts of available information in digital environments.",
            "Storytelling engages audiences through narrative structures that create emotional connections and convey messages memorably across cultures.",
            "Media effects research examines how exposure to media content influences attitudes, beliefs, and behaviors of individuals and society.",
            
            # Law, Governance, and Justice
            "Legal systems establish rules governing behavior and provide mechanisms for resolving disputes and administering justice within societies.",
            "Constitutional law defines the structure of government and protects fundamental rights that limit governmental power over individuals.",
            "Criminal justice systems investigate crimes, prosecute offenders, and impose punishments while balancing public safety with individual rights.",
            "Civil rights protect individuals from discrimination and ensure equal treatment under law regardless of race, gender, or other characteristics.",
            "International law regulates relationships between nations through treaties, customs, and institutions that promote cooperation and resolve conflicts.",
            "Environmental law addresses pollution, resource management, and conservation through regulations that balance development with protection.",
            "Corporate law governs business organizations, defining rights and responsibilities of shareholders, directors, and other stakeholders.",
            "Intellectual property law protects creative works and innovations through copyrights, patents, and trademarks that incentivize innovation.",
            "Labor law regulates employment relationships, protecting worker rights while balancing employer interests and economic considerations.",
            "Administrative law controls government agency actions, ensuring they operate within legal authority and follow fair procedures.",
            "Restorative justice emphasizes repairing harm and restoring relationships rather than only punishing offenders through traditional criminal processes.",
            "Judicial independence protects courts from political pressure, enabling judges to decide cases impartially based on law and evidence.",
            "Due process guarantees fair procedures in legal proceedings, protecting individuals from arbitrary government action and ensuring justice.",
            "Legal aid provides access to legal representation for those unable to afford attorneys, promoting equal justice under law.",
            "Alternative dispute resolution offers methods like mediation and arbitration to resolve conflicts outside formal court proceedings.",
            "Legislative processes create laws through deliberation and voting by elected representatives who balance various interests and values.",
            "Regulatory agencies implement and enforce laws through rulemaking and oversight of industries to protect public interests.",
            "Legal ethics guide professional conduct of lawyers through rules promoting competence, confidentiality, and loyalty to clients.",
            "Human rights law establishes universal standards protecting dignity and fundamental freedoms that all people possess regardless of nationality.",
            "Evidence rules determine what information can be considered in legal proceedings, balancing truth-seeking with fairness and rights protection."
        ]
        
        # Generate approximately 25,000 words with rich variety
        passage = ""
        word_count = 0
        target_words = 25000
        
        while word_count < target_words:
            sentence = random.choice(sentence_templates)
            passage += sentence + " "
            word_count += len(sentence.split())
            
            # Add connecting phrases for better flow and coherence
            if random.random() < 0.45 and word_count < target_words - 100:
                connectors = [
                    "Furthermore, ", "Moreover, ", "Additionally, ", "In addition, ", 
                    "However, ", "On the other hand, ", "Meanwhile, ", "Consequently, ",
                    "Therefore, ", "As a result, ", "For instance, ", "For example, ",
                    "Similarly, ", "Likewise, ", "In contrast, ", "Nevertheless, ",
                    "Subsequently, ", "Accordingly, ", "Specifically, ", "Particularly, ",
                    "Essentially, ", "Fundamentally, ", "Significantly, ", "Importantly, ",
                    "Notably, ", "Remarkably, ", "Interestingly, ", "Surprisingly, ",
                    "Indeed, ", "Certainly, ", "Undoubtedly, ", "Clearly, ",
                    "Evidently, ", "Obviously, ", "Naturally, ", "Alternatively, ",
                    "Simultaneously, ", "Concurrently, ", "In particular, ", "More specifically, ",
                    "That is to say, ", "In other words, ", "To put it differently, ", "To clarify, ",
                    "In fact, ", "As a matter of fact, ", "In reality, ", "Realistically, ",
                    "From this perspective, ", "In this context, ", "In this regard, ", "With respect to this, ",
                    "Building on this, ", "Expanding on this idea, ", "To elaborate, ", "To explain further, ",
                    "Conversely, ", "On the contrary, ", "By comparison, ", "Comparatively speaking, ",
                    "In summary, ", "To summarize, ", "In essence, ", "At its core, ",
                    "Ultimately, ", "In the final analysis, ", "All things considered, ", "Taking everything into account, "
                ]
                connector = random.choice(connectors)
                passage += connector
                word_count += len(connector.split())
            
            # Add paragraph breaks for readability
            if word_count % 150 < 15 and word_count > 150:
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
