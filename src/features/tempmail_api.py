#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# features/tempmail_api.py - Module xử lý API TempMail

import requests
import json

class TempMailAPI:
    """Lớp xử lý API TempMail"""
    
    BASE_URL = "https://tempmail.id.vn/api"
    
    def __init__(self, api_token):
        """
        Khởi tạo với API token
        
        Args:
            api_token (str): API token từ tempmail.id.vn
        """
        self.api_token = api_token
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_token}'
        }
    
    def get_user_info(self):
        """
        Lấy thông tin người dùng hiện tại của token
        
        Returns:
            dict: Thông tin người dùng hoặc lỗi
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/user",
                headers=self.headers
            )
            return self._handle_response(response)
        except Exception as e:
            return {'error': True, 'message': str(e)}
    
    def get_domains(self):
        """
        Lấy danh sách tên miền có sẵn
        
        Returns:
            dict: Danh sách tên miền hoặc lỗi
        """
        try:
            # Danh sách tên miền mặc định
            default_domains = [
                "tempmail.id.vn",
                "tempmail.ckvn.edu.vn",
                "nghienplus.io.vn",
                "1trick.net"
            ]
            
            # Thử gọi API
            try:
                response = requests.get(
                    f"{self.BASE_URL}/domains",
                    headers=self.headers,
                    timeout=5  # Thêm timeout 5 giây
                )
                
                # Nếu API trả về thành công
                if response.status_code == 200:
                    try:
                        domains_data = response.json()
                        print(f"DEBUG - Domains API response: {domains_data}")
                        return {'error': False, 'data': domains_data}
                    except:
                        print("DEBUG - Cannot parse domains JSON, using default domains")
                else:
                    print(f"DEBUG - Domains API error: {response.status_code}")
            except Exception as e:
                print(f"DEBUG - Domains API exception: {str(e)}")
            
            # Nếu không lấy được từ API, trả về danh sách mặc định
            print("DEBUG - Using default domains list")
            return {'error': False, 'data': default_domains}
            
        except Exception as e:
            print(f"DEBUG - get_domains exception: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def create_email(self, user=None, domain=None):
        """
        Tạo email mới
        
        Args:
            user (str, optional): Tên người dùng muốn tạo
            domain (str, optional): Tên miền cần tạo
            
        Returns:
            dict: Thông tin email đã tạo hoặc lỗi
        """
        try:
            headers = self.headers.copy()
            headers['Content-Type'] = 'application/json'
            
            data = {}
            if user:
                data['user'] = user
            if domain:
                data['domain'] = domain
            
            # Debug: In dữ liệu gửi đi
            print(f"DEBUG - Sending data to API: {data}")
                
            response = requests.post(
                f"{self.BASE_URL}/email/create",
                headers=headers,
                data=json.dumps(data) if data else None
            )
            
            # Debug: In phản hồi từ API
            print(f"DEBUG - API Response Status: {response.status_code}")
            print(f"DEBUG - API Response Headers: {response.headers}")
            try:
                print(f"DEBUG - API Response Body: {response.text}")
            except:
                print("DEBUG - Cannot print response body")
                
            result = self._handle_response(response)
            
            # Kiểm tra và xử lý dữ liệu đặc biệt
            if not result['error'] and 'data' in result:
                if isinstance(result['data'], str):
                    # Nếu API trả về chuỗi, chuyển thành đối tượng với trường email
                    result['data'] = {'email': result['data']}
                    
            return result
        except Exception as e:
            print(f"DEBUG - Exception in create_email: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def get_email_list(self):
        """
        Lấy danh sách email của người dùng
        
        Returns:
            dict: Danh sách email hoặc lỗi
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/email",
                headers=self.headers
            )
            
            # Debug: In phản hồi từ API
            print(f"DEBUG - API Response Status: {response.status_code}")
            try:
                print(f"DEBUG - API Response Body: {response.text}")
            except:
                print("DEBUG - Cannot print response body")
                
            result = self._handle_response(response)

            # Kiểm tra và xử lý dữ liệu đặc biệt
            if not result['error'] and 'data' in result:
                data = result['data']

                # Nếu API trả về cấu trúc {'success': True, 'data': [...]}
                if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                    print(f"DEBUG - get_email_list: Found nested data structure")
                    # Trả về danh sách email trực tiếp
                    return {'error': False, 'data': data['data']}
                elif isinstance(data, list):
                    print(f"DEBUG - get_email_list: Found direct list")
                    # Xử lý từng phần tử trong danh sách
                    for i, item in enumerate(data):
                        if isinstance(item, str):
                            # Nếu phần tử là chuỗi, chuyển thành đối tượng với trường email
                            data[i] = {'email': item}
                    return {'error': False, 'data': data}

            return result
        except Exception as e:
            print(f"DEBUG - Exception in get_email_list: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def get_messages(self, mail_id):
        """
        Lấy danh sách thư của một email
        
        Args:
            mail_id (str): ID của email
            
        Returns:
            dict: Danh sách thư hoặc lỗi
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/email/{mail_id}",
                headers=self.headers
            )
            
            # Debug: In phản hồi từ API
            print(f"DEBUG - API Response Status (get_messages): {response.status_code}")
            try:
                print(f"DEBUG - API Response Body (get_messages): {response.text}")
            except:
                print("DEBUG - Cannot print response body")
            
            result = self._handle_response(response)

            # Debug: In ra kết quả xử lý
            print(f"DEBUG - get_messages result: {result}")

            # Xử lý đặc biệt cho danh sách thư
            if not result['error']:
                data = result['data']
                print(f"DEBUG - get_messages data type: {type(data)}")
                print(f"DEBUG - get_messages data content: {data}")

                if isinstance(data, dict):
                    # Kiểm tra cấu trúc {'success': True, 'data': {'items': [...], 'pagination': {...}}}
                    if 'success' in data and 'data' in data and isinstance(data['data'], dict):
                        nested_data = data['data']
                        print(f"DEBUG - Found nested success structure with keys: {list(nested_data.keys())}")

                        if 'items' in nested_data and isinstance(nested_data['items'], list):
                            print(f"DEBUG - Found items array with {len(nested_data['items'])} items")
                            return {'error': False, 'data': nested_data['items']}

                    # Nếu API trả về cấu trúc {'items': [...], 'pagination': {...}}
                    elif 'items' in data and isinstance(data['items'], list):
                        print(f"DEBUG - Found items array with {len(data['items'])} items")
                        # Trả về danh sách thư trực tiếp
                        return {'error': False, 'data': data['items']}

                    # Nếu API trả về cấu trúc {'data': [...]}
                    elif 'data' in data and isinstance(data['data'], list):
                        print(f"DEBUG - Found nested data array with {len(data['data'])} items")
                        return {'error': False, 'data': data['data']}

                    # Nếu API trả về cấu trúc {'success': True, 'data': [...]}
                    elif 'success' in data and 'data' in data and isinstance(data['data'], list):
                        print(f"DEBUG - Found success structure with data array: {len(data['data'])} items")
                        return {'error': False, 'data': data['data']}

                    else:
                        print(f"DEBUG - Dict structure not recognized, keys: {list(data.keys())}")
                        # Trả về toàn bộ dict để debug
                        return {'error': False, 'data': data}

                elif isinstance(data, list):
                    print(f"DEBUG - Direct list with {len(data)} items")
                    return {'error': False, 'data': data}
                else:
                    print(f"DEBUG - Unknown data type: {type(data)}")

            return result
        except Exception as e:
            print(f"DEBUG - Exception in get_messages: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def get_message_content(self, message_id):
        """
        Đọc nội dung của một thư
        
        Args:
            message_id (str): ID của thư
            
        Returns:
            dict: Nội dung thư hoặc lỗi
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/message/{message_id}",
                headers=self.headers
            )
            
            # Debug: In phản hồi từ API
            print(f"DEBUG - API Response Status (get_message_content): {response.status_code}")
            try:
                print(f"DEBUG - API Response Body (get_message_content): {response.text[:200]}...")
            except:
                print("DEBUG - Cannot print response body")
            
            result = self._handle_response(response)
            
            # Xử lý đặc biệt cho nội dung thư
            if not result['error']:
                # Nếu API trả về trực tiếp nội dung HTML
                if isinstance(result['data'], str) and (result['data'].startswith('<!DOCTYPE') or result['data'].startswith('<html')):
                    # Đóng gói trong một đối tượng dict
                    return {'error': False, 'data': {'html': result['data'], 'text': ''}}
                
                # Nếu API trả về đối tượng JSON
                if isinstance(result['data'], dict):
                    # Kiểm tra xem có cấu trúc đặc biệt không
                    if 'html' in result['data'] or 'text' in result['data']:
                        # Đã có định dạng đúng
                        return result
                    elif 'body' in result['data']:
                        # Chuyển đổi 'body' thành 'html' hoặc 'text'
                        body = result['data']['body']
                        if body.startswith('<!DOCTYPE') or body.startswith('<html'):
                            result['data']['html'] = body
                        else:
                            result['data']['text'] = body
                        return result
            
            return result
        except Exception as e:
            print(f"DEBUG - Exception in get_message_content: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def delete_email(self, mail_id):
        """
        Xóa một email - Thử nhiều phương thức khác nhau

        Args:
            mail_id (str): ID của email cần xóa

        Returns:
            dict: Kết quả xóa email hoặc lỗi
        """
        try:
            # Phương thức 1: Thử DELETE method (phương thức chuẩn)
            print(f"DEBUG - Trying DELETE method for email {mail_id}")
            response = requests.delete(
                f"{self.BASE_URL}/email/{mail_id}",
                headers=self.headers
            )

            print(f"DEBUG - DELETE Response Status: {response.status_code}")
            print(f"DEBUG - DELETE Response Body: {response.text}")

            # Nếu DELETE thành công (status 200 hoặc 204)
            if response.status_code in [200, 204]:
                return self._handle_response(response)

            # Nếu DELETE không được hỗ trợ (405 Method Not Allowed)
            if response.status_code == 405:
                print(f"DEBUG - DELETE method not supported, trying POST method")

                # Phương thức 2: Thử POST với action delete
                headers = self.headers.copy()
                headers['Content-Type'] = 'application/json'

                delete_data = {
                    'action': 'delete',
                    'mail_id': mail_id
                }

                response = requests.post(
                    f"{self.BASE_URL}/email/{mail_id}/delete",
                    headers=headers,
                    data=json.dumps(delete_data)
                )

                print(f"DEBUG - POST delete Response Status: {response.status_code}")
                print(f"DEBUG - POST delete Response Body: {response.text}")

                if response.status_code in [200, 204]:
                    return self._handle_response(response)

                # Phương thức 3: Thử POST với endpoint khác
                response = requests.post(
                    f"{self.BASE_URL}/email/delete",
                    headers=headers,
                    data=json.dumps({'id': mail_id})
                )

                print(f"DEBUG - POST delete alternative Response Status: {response.status_code}")
                print(f"DEBUG - POST delete alternative Response Body: {response.text}")

                if response.status_code in [200, 204]:
                    return self._handle_response(response)

            # Nếu tất cả phương thức đều thất bại
            return {
                'error': True,
                'message': f'API không hỗ trợ xóa email. Phương thức DELETE trả về: {response.status_code}. Bạn có thể xóa email thủ công trên website tempmail.id.vn',
                'status': response.status_code,
                'unsupported': True  # Flag để GUI biết đây là lỗi không hỗ trợ
            }

        except Exception as e:
            print(f"DEBUG - Exception in delete_email: {str(e)}")
            return {'error': True, 'message': str(e)}

    def check_delete_support(self):
        """
        Kiểm tra xem API có hỗ trợ xóa email không

        Returns:
            dict: Thông tin về khả năng hỗ trợ xóa email
        """
        try:
            # Thử gọi OPTIONS method để kiểm tra các phương thức được hỗ trợ
            response = requests.options(
                f"{self.BASE_URL}/email/test",
                headers=self.headers
            )

            allowed_methods = response.headers.get('Allow', '').upper()
            supports_delete = 'DELETE' in allowed_methods

            print(f"DEBUG - Allowed methods: {allowed_methods}")
            print(f"DEBUG - Supports DELETE: {supports_delete}")

            return {
                'error': False,
                'supports_delete': supports_delete,
                'allowed_methods': allowed_methods,
                'message': 'DELETE được hỗ trợ' if supports_delete else 'DELETE không được hỗ trợ'
            }

        except Exception as e:
            print(f"DEBUG - Exception in check_delete_support: {str(e)}")
            return {
                'error': True,
                'supports_delete': False,
                'message': f'Không thể kiểm tra: {str(e)}'
            }

    def _handle_response(self, response):
        """
        Xử lý phản hồi từ API
        
        Args:
            response (Response): Đối tượng phản hồi từ requests
            
        Returns:
            dict: Dữ liệu phản hồi hoặc lỗi
        """
        try:
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {'error': False, 'data': data}
                except json.JSONDecodeError:
                    # Nếu không phải JSON, trả về chuỗi
                    return {'error': False, 'data': response.text}
            else:
                try:
                    error_data = response.json()
                    return {'error': True, 'message': error_data.get('message', 'Lỗi không xác định'), 'status': response.status_code}
                except:
                    return {'error': True, 'message': f'Lỗi: {response.status_code}', 'status': response.status_code}
        except Exception as e:
            return {'error': True, 'message': str(e)}

# Hàm test
if __name__ == "__main__":
    # Chỉ để minh họa, không chạy trực tiếp
    api = TempMailAPI("your_api_token_here")
    print("Thông tin người dùng:", api.get_user_info())
    print("Danh sách tên miền:", api.get_domains())
    print("Tạo email mới:", api.create_email()) 