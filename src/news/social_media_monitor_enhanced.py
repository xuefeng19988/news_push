#!/usr/bin/env python3
"""
增强版社交媒体监控 - 支持微博、Twitter、Reddit等平台
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import re

class SocialMediaMonitor:
    """社交媒体监控器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 社交媒体平台配置
        self.platforms = [
            {
                'name': '微博热搜',
                'type': 'weibo',
                'url': 'https://weibo.com/ajax/side/hotSearch',
                'enabled': True,
                'check_interval': 30  # 分钟
            },
            {
                'name': 'Reddit热门',
                'type': 'reddit',
                'url': 'https://www.reddit.com/r/all/hot.json',
                'enabled': True,
                'check_interval': 60
            },
            {
                'name': 'Twitter趋势',
                'type': 'twitter',
                'url': 'https://api.twitter.com/1.1/trends/place.json?id=1',
                'enabled': False,  # 需要API密钥
                'check_interval': 60
            }
        ]
        
        # 存储历史数据
        self.history_file = "/home/admin/clawd/social_media_history.json"
        self.history = self.load_history()
    
    def load_history(self) -> Dict:
        """加载历史数据"""
        try:
            import os
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"trends": {}, "last_check": {}}
        except:
            return {"trends": {}, "last_check": {}}
    
    def save_history(self):
        """保存历史数据"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存历史数据失败: {e}")
    
    def fetch_weibo_trends(self) -> List[Dict]:
        """获取微博热搜"""
        try:
            headers = {
                'Referer': 'https://weibo.com/',
                'Accept': 'application/json, text/plain, */*'
            }
            
            response = self.session.get(
                'https://weibo.com/ajax/side/hotSearch',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trends = []
                
                if 'data' in data and 'realtime' in data['data']:
                    for item in data['data']['realtime'][:15]:  # 取前15条
                        word = item.get('word', '').strip()
                        if not word:
                            continue
                        
                        # 热度值
                        hot_value = item.get('num', 0)
                        label_desc = item.get('label_name', '')
                        
                        # 生成URL
                        encoded_word = requests.utils.quote(word)
                        url = f"https://s.weibo.com/weibo?q={encoded_word}"
                        
                        trends.append({
                            'platform': '微博',
                            'title': f"#{word}",
                            'url': url,
                            'hot_value': hot_value,
                            'label': label_desc,
                            'rank': item.get('rank', 0),
                            'timestamp': datetime.now().isoformat()
                        })
                
                return trends
            else:
                print(f"❌ 微博API错误: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 获取微博热搜失败: {e}")
            return []
    
    def fetch_reddit_hot(self) -> List[Dict]:
        """获取Reddit热门帖子"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = self.session.get(
                'https://www.reddit.com/r/popular/hot.json?limit=15',
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                if 'data' in data and 'children' in data['data']:
                    for child in data['data']['children'][:15]:
                        post_data = child.get('data', {})
                        
                        title = post_data.get('title', '').strip()
                        if not title:
                            continue
                        
                        # 清理标题
                        title = re.sub(r'\[.*?\]', '', title)  # 移除标签
                        title = title[:120]  # 限制长度
                        
                        # 获取完整URL
                        permalink = post_data.get('permalink', '')
                        url = f"https://reddit.com{permalink}" if permalink else post_data.get('url', '')
                        
                        # 统计信息
                        ups = post_data.get('ups', 0)
                        comments = post_data.get('num_comments', 0)
                        subreddit = post_data.get('subreddit', '')
                        
                        posts.append({
                            'platform': 'Reddit',
                            'title': title,
                            'url': url,
                            'subreddit': f"r/{subreddit}",
                            'upvotes': ups,
                            'comments': comments,
                            'score': post_data.get('score', 0),
                            'timestamp': datetime.now().isoformat()
                        })
                
                return posts
            else:
                print(f"❌ Reddit API错误: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 获取Reddit热门失败: {e}")
            return []
    
    def fetch_twitter_trends(self) -> List[Dict]:
        """获取Twitter趋势（需要API密钥）"""
        # Twitter API v2需要认证，这里返回空列表
        print("⚠️ Twitter API需要OAuth认证，跳过")
        return []
    
    def fetch_all_social_media(self) -> Dict[str, List[Dict]]:
        """获取所有社交媒体数据"""
        print("📱 开始获取社交媒体数据...")
        
        results = {}
        
        for platform in self.platforms:
            if not platform['enabled']:
                continue
            
            print(f"  获取 {platform['name']}...")
            
            if platform['type'] == 'weibo':
                trends = self.fetch_weibo_trends()
                if trends:
                    results['weibo'] = trends
                    print(f"    ✅ 成功: {len(trends)} 条热搜")
                else:
                    print(f"    ❌ 失败")
            
            elif platform['type'] == 'reddit':
                posts = self.fetch_reddit_hot()
                if posts:
                    results['reddit'] = posts
                    print(f"    ✅ 成功: {len(posts)} 条热门")
                else:
                    print(f"    ❌ 失败")
            
            elif platform['type'] == 'twitter':
                trends = self.fetch_twitter_trends()
                if trends:
                    results['twitter'] = trends
                    print(f"    ✅ 成功: {len(trends)} 条趋势")
            
            time.sleep(1)  # 避免请求过快
        
        return results
    
    def analyze_trends(self, social_data: Dict[str, List[Dict]]) -> Dict:
        """分析社交媒体趋势"""
        analysis = {
            'total_trends': 0,
            'platforms': [],
            'hot_topics': [],
            'summary': ''
        }
        
        for platform, trends in social_data.items():
            if trends:
                analysis['platforms'].append({
                    'name': platform,
                    'count': len(trends),
                    'top_trend': trends[0]['title'] if trends else '无'
                })
                analysis['total_trends'] += len(trends)
                
                # 收集热门话题
                for trend in trends[:3]:
                    analysis['hot_topics'].append({
                        'platform': platform,
                        'title': trend['title'],
                        'hot_value': trend.get('hot_value', trend.get('upvotes', 0))
                    })
        
        # 生成摘要
        if analysis['total_trends'] > 0:
            platform_names = [p['name'] for p in analysis['platforms']]
            analysis['summary'] = f"共监测到 {analysis['total_trends']} 条趋势，来自 {len(platform_names)} 个平台"
        else:
            analysis['summary'] = "未获取到社交媒体数据"
        
        return analysis
    
    def format_social_report(self, social_data: Dict[str, List[Dict]], analysis: Dict) -> str:
        """格式化社交媒体报告"""
        if not social_data:
            return "📭 暂时没有社交媒体数据\n"
        
        report = "💬 **社交媒体动态**\n\n"
        
        # 按平台显示
        for platform, trends in social_data.items():
            if not trends:
                continue
            
            # 平台标题
            platform_emoji = {
                'weibo': '🐦',
                'reddit': '👾',
                'twitter': '🐦'
            }.get(platform, '💬')
            
            platform_name = {
                'weibo': '微博热搜',
                'reddit': 'Reddit热门',
                'twitter': 'Twitter趋势'
            }.get(platform, platform)
            
            report += f"{platform_emoji} **{platform_name}**\n"
            
            # 显示前5条
            for i, trend in enumerate(trends[:5], 1):
                title = trend['title']
                
                # 添加热度信息
                if platform == 'weibo':
                    hot_value = trend.get('hot_value', 0)
                    if hot_value > 1000000:
                        hot_str = f"{hot_value/10000:.1f}万"
                    elif hot_value > 1000:
                        hot_str = f"{hot_value/1000:.1f}千"
                    else:
                        hot_str = str(hot_value)
                    
                    report += f"  {i}. {title} 🔥{hot_str}\n"
                
                elif platform == 'reddit':
                    upvotes = trend.get('upvotes', 0)
                    comments = trend.get('comments', 0)
                    subreddit = trend.get('subreddit', '')
                    
                    report += f"  {i}. {title}\n"
                    report += f"     👍 {upvotes} | 💬 {comments} | {subreddit}\n"
            
            report += "\n"
        
        # 分析摘要
        report += "📊 **趋势分析**\n"
        report += f"• 总趋势数: {analysis['total_trends']}\n"
        
        for platform_info in analysis['platforms']:
            report += f"• {platform_info['name']}: {platform_info['count']}条\n"
        
        # 热门话题
        if analysis['hot_topics']:
            report += "\n🔥 **热门话题**:\n"
            for topic in analysis['hot_topics'][:3]:
                report += f"• {topic['platform']}: {topic['title']}\n"
        
        report += f"\n⏰ 更新时间: {datetime.now().strftime('%H:%M')}\n"
        
        return report
    
    def check_and_report(self) -> Optional[str]:
        """检查并生成报告"""
        print(f"\n{'='*60}")
        print(f"📱 社交媒体监控启动")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 获取数据
            social_data = self.fetch_all_social_media()
            
            if not social_data:
                print("📭 未获取到社交媒体数据")
                return None
            
            # 分析数据
            analysis = self.analyze_trends(social_data)
            
            # 生成报告
            report = self.format_social_report(social_data, analysis)
            
            # 保存历史
            self.history['last_check'] = {
                'timestamp': datetime.now().isoformat(),
                'platforms': list(social_data.keys()),
                'total_trends': analysis['total_trends']
            }
            self.save_history()
            
            print(f"\n✅ 社交媒体监控完成!")
            print(f"   报告长度: {len(report)} 字符")
            print(f"   平台数量: {len(social_data)}")
            print(f"   总趋势数: {analysis['total_trends']}")
            
            return report
            
        except Exception as e:
            print(f"❌ 社交媒体监控失败: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """主函数"""
    monitor = SocialMediaMonitor()
    report = monitor.check_and_report()
    
    if report:
        print(f"\n📄 报告预览:")
        print("-"*40)
        print(report[:300] + "..." if len(report) > 300 else report)
        print("-"*40)
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_file = f"./logs/social_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 报告已保存: {report_file}")
        return True
    else:
        print("❌ 未生成报告")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)