import os


class BaseDataConfig:
    least_fav_topic_count = 4
    val_split_pct = 0.2


class BaseConfig:
    """General configuration."""

    num_epochs = 2
    num_batches_show_loss = 100  # Number of batchs to show loss
    # Number of batchs to check metrics on validation dataset
    num_batches_validate = 1000
    batch_size = 128
    learning_rate = 0.0001
    num_workers = os.cpu_count()  # Number of workers for data loading
    num_clicked_news_a_user = 50  # Number of sampled click history for each user
    num_words_title = 20
    num_words_abstract = 50
    word_freq_threshold = 1
    entity_freq_threshold = 2
    entity_confidence_threshold = 0.5
    negative_sampling_ratio = 2  # K
    dropout_probability = 0.2
    # Modify the following by the output of `src/dataprocess.py`
    num_words = 1 + 70975
    num_categories = 1 + 274
    num_entities = 1 + 12957
    num_users = 1 + 50000
    word_embedding_dim = 300
    category_embedding_dim = 100
    # Modify the following only if you use another dataset
    entity_embedding_dim = 100
    # For additive attention
    query_vector_dim = 200


class TANRConfig(BaseConfig, BaseDataConfig):
    dataset_attributes = {"news": ["category", "title"], "record": []}
    # For CNN
    num_filters = 300
    window_size = 3
    topic_classification_loss_weight = 0.1
