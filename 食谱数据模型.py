"""食谱数据模型"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()

class Recipe(db.Model):
    """食谱模型"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False, comment='食谱标题')
    description = db.Column(db.Text, comment='食谱描述')
    cover_image = db.Column(db.String(500), comment='封面图片URL')
    
    # 分类信息
    category = db.Column(db.String(50), comment='分类：家常菜、汤羹、甜品等')
    cuisine = db.Column(db.String(50), comment='菜系：中式、西式、日式等')
    difficulty = db.Column(db.String(20), default='中等', comment='难度：简单、中等、困难')
    prep_time = db.Column(db.Integer, comment='准备时间（分钟）')
    cook_time = db.Column(db.Integer, comment='烹饪时间（分钟）')
    servings = db.Column(db.Integer, default=2, comment='份量')
    
    # 内容
    ingredients = db.Column(db.Text, nullable=False, comment='食材列表（JSON格式）')
    steps = db.Column(db.Text, nullable=False, comment='制作步骤（JSON格式）')
    tips = db.Column(db.Text, comment='小贴士')
    
    # 营养信息（可选）
    calories = db.Column(db.Integer, comment='卡路里')
    nutrition_info = db.Column(db.Text, comment='营养信息JSON')
    
    # 用户信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建用户ID')
    author_name = db.Column(db.String(100), comment='作者姓名（显示用）')
    
    # 统计信息
    views = db.Column(db.Integer, default=0, comment='浏览量')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    saves = db.Column(db.Integer, default=0, comment='收藏数')
    
    # 状态
    status = db.Column(db.String(20), default='published', comment='状态：draft, published, hidden')
    is_featured = db.Column(db.Boolean, default=False, comment='是否推荐')
    is_verified = db.Column(db.Boolean, default=False, comment='是否官方验证')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='recipes')
    comments = db.relationship('RecipeComment', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    recipe_products = db.relationship('RecipeProduct', backref='recipe', lazy='dynamic')
    
    def __repr__(self):
        return f'<Recipe {self.title}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'author': self.author_name or (self.user.username if self.user else '匿名'),
            'category': self.category,
            'difficulty': self.difficulty,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'views': self.views,
            'likes': self.likes,
            'cover_image': self.cover_image,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'ingredients': json.loads(self.ingredients) if self.ingredients else [],
            'steps': json.loads(self.steps) if self.steps else []
        }
    
    def get_ingredients_list(self):
        """获取食材列表"""
        if self.ingredients:
            return json.loads(self.ingredients)
        return []
    
    def get_steps_list(self):
        """获取步骤列表"""
        if self.steps:
            return json.loads(self.steps)
        return []


class RecipeComment(db.Model):
    """食谱评论模型"""
    __tablename__ = 'recipe_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5, comment='评分1-5')
    likes = db.Column(db.Integer, default=0)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='recipe_comments')
    
    def __repr__(self):
        return f'<RecipeComment {self.id}>'


class RecipeProduct(db.Model):
    """食谱关联产品（用户可以选择食谱中使用的农产品）"""
    __tablename__ = 'recipe_products'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.String(50), comment='用量：如"200g"、"2个"')
    note = db.Column(db.String(200), comment='备注')
    
    # 关系
    product = db.relationship('Product', backref='used_in_recipes')
    
    def __repr__(self):
        return f'<RecipeProduct {self.id}>'


class RecipeCollection(db.Model):
    """食谱收藏"""
    __tablename__ = 'recipe_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束：一个用户只能收藏一次同一个食谱
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_collection'),
    )
    
    def __repr__(self):
        return f'<RecipeCollection {self.id}>'


class RecipeLike(db.Model):
    """食谱点赞"""
    __tablename__ = 'recipe_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_like'),
    )
    
    def __repr__(self):
        return f'<RecipeLike {self.id}>'
