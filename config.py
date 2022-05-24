HACKERNEWS_API = """https://hackernews-app.s3.us-east-1.amazonaws.com/topic_data_pred.json?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIz%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCppXlnx3QhW06%2FcIx5dfhBowGXZxAHI5MR9euIIkVa%2BwIhAPj7rLx6gANH1FDYxVHuNC1Yylk4Ug%2BQk7EC1ni5GKmTKt0DCHUQAhoMODIyNDc4ODk1ODg2IgyOlH0OEMU%2FBuh98Y8qugMplCvbOzSMg7UyGtliBq9fQnbOMAT%2BxQ6%2BIV2KgS7QD%2BnXzKbAALSQwYNjgTR%2FSOGFXs4KzV5w4fZ%2FTbT6FM%2Bjeu0Pt2CxfAb%2BxyNijZhoSYTVA0Ofzw9zFVBSVi%2BIatVW1TKhC5O6iANO0Y%2FscuRLiI1aaMVaqDGFgmnIRZJsThulIbYduWueQIS85RAsDUvGfNIX8fZaHed8bGLNpbZEBCLzHvkeOw01fn%2BCEiDxB3dCzbALjT6AlckRnnt3%2Ba4rKbMfJhBNnEXBFpDECXbmW2serWgpWSIVbi6HkD2YvZdg70NPSi5GIXIroq66C5BdjLxyqCalHusoLkkGdwdQd7w1dQoBk9RuEFRHpvAuU7CiG%2FbQP7qXPWZ4vGS3EwlkivhKiN2zeWGxLCcTXM5duHl2xkzeYY5s6eRvBZ7kbETcnYOiP7Exs30ejGLd0ejpmc78Q0myis6TjQRinptp%2FA0qQp9avMlsv6npEKlQ%2F62bezJMGWjIHtrSOO8PUMgKFZwTKvQizDZmxmJ6AMzIKeQ0ftvTCe2RZT8ux7dGBwHbv1Yg80G84Ap6jzOdxPpto0jxT1Cc%2BPUWMOeIs5QGOpMCbgJ%2BApdDabBZhIXfPQPpe6ueRNrMoSn04ESgNSY8xEEpbWljcmpRt1KedUDkxEuAt8DZ7%2FaaKBDC29CCfX2%2F6kLkhdH8nxOitKlwIGm8Q6avaGw7mQWpjsXNzBURiHrg6L7Dgyd8mJnUKSyaXxuAB2ADa0XhgZptjIE2S6KRZ44G00P2fLa%2FmW2xJo8gzIEJTjUreT82STYIOcPqvj7WnwNzcmCZ8neQrdSFJW4HIlJolaFxlzOITu9b5bgiVDPuK4%2FhiEbIbv1%2Fp1Q23u49uyEhOtmOZ73M8vVjsT8gHs%2FO5N68B2q847gJOZzggZ%2B%2BkwE5miz%2BnRT7tWsgOOZh1d%2FYPcxdVIPgyHmuBdxwJ%2FPeRXk%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220524T115125Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIA3674P7MHIZ4Q4OBN%2F20220524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=0c4e6bec81cb105fcaf7403299c5ef058bf8932dcbfe34485c4cf9e0a1518a7d"""


class BaseConfig:
    """General configuration."""

    num_epochs = 2
    num_batches_show_loss = 100  # Number of batchs to show loss
    # Number of batchs to check metrics on validation dataset
    num_batches_validate = 1000
    batch_size = 128
    learning_rate = 0.0001
    num_workers = 4  # Number of workers for data loading
    num_clicked_news_a_user = 50  # Number of sampled click history for each user
    num_words_title = 20
    word_freq_threshold = 1
    entity_freq_threshold = 2
    entity_confidence_threshold = 0.5
    negative_sampling_ratio = 2  # K
    dropout_probability = 0.2
    word_embedding_dim = 300
    # Modify the following only if you use another dataset
    entity_embedding_dim = 100
    # For additive attention
    query_vector_dim = 200
    # For CNN
    num_filters = 300
    window_size = 3
