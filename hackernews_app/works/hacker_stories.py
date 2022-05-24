import json

from lightning.storage import Path
from lightning import LightningWork
from hackernews import HackerNews


class HackerStories(LightningWork):
    
    def __init__(self, category: str = "new", num_stories: int = 100) -> None:
        super().__init__()
        
        hn = HackerNews()
        self.stories_categories = {
            "top": hn.top_stories,
            "new": hn.new_stories,
        }
        self.stories_storage_path = Path("stories.json")
        self._category = category
        self._num_stories = num_stories
        
    def run(self):
        stories = self.stories_categories[self._category](limit=self._num_stories)
        
        stories_data_list = []
        
        for story in stories:
            story_data = {}
            story_data["item_id"] = story.item_id
            story_data["title"] = story.title
            story_data["text"] = story.text or ""
            story_data["total_text"] = story_data["title"] + story_data["text"]
            story_data["url"] = story.url
            story_data["score"] = story.score

            stories_data_list.append(story_data)
            
        with open(self.stories_storage_path, "w") as fp:
            json.dump(stories, fp)
        
        
        