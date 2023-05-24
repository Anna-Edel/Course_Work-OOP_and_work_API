import requests
import json
import datetime
from tqdm import tqdm


def write_json(data):  # получение списка фотографий со страницы в VK в формате json
    with open('list_photos_VK.json', 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_foto_data(offset=0, count=50):  # получение списка фотографий со страницы в VK
    api = requests.get('https://api.vk.com/method/photos.getAll', params={
        'owner_id': vk_user_id,
        'access_token': vk_token,
        'offset': offset,
        'count': count,
        'extended': 1,
        'photo_sizes': True,
        'v': 5.131

    })
    write_json(api.json())
    return json.loads(api.text)


def get_largest(size_dict):
    """ Определение ориентации фотографии  """
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    else:
        return size_dict['height']


def time_conversion(unix_time):
    """ Преобразование времени из формата Unix-времени в обычную дату и время в формате строки. """
    value = datetime.datetime.fromtimestamp(unix_time)
    time_value = value.strftime('%Y-%m-%d time %H-%M-%S')
    return time_value


class YaUploader:

    def __init__(self, token: str):
        self.token = token

    def creating_folder(self, file_path):
        """ Создание папки на Яндекс.Диске """
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {"path": file_path}
        headers = {'Content-Type': 'application/json', 'Authorization': ya_token}
        response = requests.put(url=upload_url, headers=headers, params=params)

    def upload(self, file_path, url_vk):
        """  Загрузка файла на Яндекс.Диск """
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": file_path, "url": url_vk}
        headers = {'Content-Type': 'application/json', 'Authorization': ya_token}
        response = requests.post(url=upload_url, headers=headers, params=params)
        json_resp = response.json()
        href = json_resp.get('href', '')
        resp = requests.get(url=href, headers=headers, params=params)
        resp.raise_for_status()


class YA_token:
    pass


def main():
    global size
    get_foto_data()  # получение списка фотографий со страницы в VK и сохранение его в файл 'list_photos_VK.json'
    photos = json.load(open('list_photos_VK.json'))['response']['items']
    json_list = []
    name_url_photos_dict = {}
    number = 0
    for photo in photos:  # заполнение словаря: кол-во лайков, дата загрузки фотографий, URL фотографии в vk
        sizes = photo['sizes']
        likes = photo['likes']
        max_size_url = max(sizes, key=get_largest)['url']  # определяет фотографию с максимальным размером
        for numb_url in sizes:
            if numb_url['url'] == max_size_url:
                size = numb_url['type']

        if likes['count'] == 0 or likes['count'] == number:  # определяется количество лайков
            unix_time = photo['date']
            key_photo = time_conversion(unix_time)

        else:
            key_photo = likes['count']
            number = likes['count']

        file_name = f'{key_photo}.jpg'
        json_list.append({'file name': file_name, 'size': size})
        name_url_photos_dict[key_photo] = max_size_url
        """ Список словарей json_list, где каждый словарь содержит информацию о имени файла, размере и соответствующем 
            URL-адресе фотографии в максимальном размере."""

    create_fold = YaUploader(ya_token)
    create_fold.creating_folder(path_to_file)
    num = int(input('Введите количество фотографий для загрузки на Яндекс Диск (от 1 до 5 фото.)\n'))
    json_list_result = []
    for name_photo, i in zip(name_url_photos_dict.keys(), tqdm(range(num))):
        uploader = YaUploader(ya_token)
        uploader.upload(f'{path_to_file}/{name_photo}', name_url_photos_dict[name_photo])
        json_list_result.append(json_list[int(i - 1)])
    with open('uploaded_VK_photos.json', 'w') as file:
        json.dump(json_list_result, file)  # весь список json_list_result сохраняется в файле 'uploaded_VK_photos.json'

    print()
    print(f'На Яндекс.Диск загружено: {num} фото.')


if __name__ == "__main__":

    """Открывается файл "id_VK_and_tokens_VK_and_Ya_disk.txt", 
    где пользователь ввел vk_user_id, vk_token и ya_token"""

    with open('id_VK_and_tokens_VK_and_Ya_disk.txt') as f:
        vk_user_id = f.readline().strip()
        vk_token = f.readline().strip()
        ya_token = f.read().strip()
    path_to_file = input("Введите название папки на Яндекс.Диске\n")
    main()

