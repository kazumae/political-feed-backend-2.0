"""
トピックテストデータ作成モジュール
"""
import random

from app.models.topic import Topic, TopicRelation
from sqlalchemy.orm import Session


def create_test_topics(db: Session):
    """
    テスト用のトピックデータを作成
    """
    print("トピックデータを作成中...")
    
    topics_data = [
        {
            "name": "経済政策",
            "slug": "economy",
            "description": "経済成長、財政政策、金融政策などに関するトピック",
            "category": "economy",
            "importance": 90,
            "icon_url": "https://example.com/icons/economy.png",
            "color_code": "#00ff00",
        },
        {
            "name": "外交・安全保障",
            "slug": "foreign_policy",
            "description": "外交関係、安全保障政策、防衛政策などに関するトピック",
            "category": "foreign_policy",
            "importance": 85,
            "icon_url": "https://example.com/icons/foreign_policy.png",
            "color_code": "#0000ff",
        },
        {
            "name": "社会保障",
            "slug": "social_welfare",
            "description": "医療、年金、介護、生活保護などに関するトピック",
            "category": "social_welfare",
            "importance": 80,
            "icon_url": "https://example.com/icons/social_welfare.png",
            "color_code": "#ff00ff",
        },
        {
            "name": "教育",
            "slug": "education",
            "description": "学校教育、高等教育、教育改革などに関するトピック",
            "category": "education",
            "importance": 75,
            "icon_url": "https://example.com/icons/education.png",
            "color_code": "#ffff00",
        },
        {
            "name": "環境・エネルギー",
            "slug": "environment",
            "description": "環境保護、気候変動対策、エネルギー政策などに関するトピック",
            "category": "environment",
            "importance": 70,
            "icon_url": "https://example.com/icons/environment.png",
            "color_code": "#00ffff",
        },
    ]
    
    topic_objects = []
    for topic_data in topics_data:
        topic = Topic(
            name=topic_data["name"],
            slug=topic_data["slug"],
            description=topic_data["description"],
            category=topic_data["category"],
            importance=topic_data["importance"],
            icon_url=topic_data["icon_url"],
            color_code=topic_data["color_code"],
            status="active",
        )
        db.add(topic)
        topic_objects.append(topic)
    
    db.commit()
    
    # トピック間の関連を作成
    for i in range(len(topic_objects)):
        for j in range(i + 1, len(topic_objects)):
            relation_type = ["related", "parent_child", "opposite"][random.randint(0, 2)]
            
            # 関連の強さをランダムに設定
            strength = random.randint(30, 90)
            
            topic_relation = TopicRelation(
                parent_topic_id=topic_objects[i].id,
                child_topic_id=topic_objects[j].id,
                relation_type=relation_type,
                strength=strength,
            )
            db.add(topic_relation)
    
    db.commit()
    print(f"トピックデータを作成しました: {len(topics_data)}件")
    return topic_objects