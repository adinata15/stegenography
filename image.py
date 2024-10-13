from PIL import Image

def hide_text(image_path, secret_text, output_path):
	# Open the image
	image = Image.open(image_path)

	# Convert the secret text to binary
	# Data length + data (with tab as delimiter)
	binary_secret_text = ''
	for char in str(len(secret_text)):
		binary_secret_text += str(format(ord(char), '08b'))

	binary_secret_text += str(format(ord('\t'), '08b'))
	
	for char in secret_text:
		binary_secret_text += format(ord(char), '08b')
	
	binary_secret_text += str(format(ord('\t'), '08b'))

	# Check if the image can accommodate the secret text
	image_capacity = image.width * image.height * 3
	if len(binary_secret_text) > image_capacity:
		raise ValueError("Image does not have sufficient capacity to hide the secret text.")

	# Hide the secret text in the image
	pixels = image.load()
	index = 0
	for i in range(image.width):
		for j in range(image.height):
			r, g, b = pixels[i, j]

			# Modify the least significant bit of each color channel
			if index < len(binary_secret_text):
				r = (r & 0xFE) | int(binary_secret_text[index])
				index += 1
			if index < len(binary_secret_text):
				g = (g & 0xFE) | int(binary_secret_text[index])
				index += 1
			if index < len(binary_secret_text):
				b = (b & 0xFE) | int(binary_secret_text[index])
				index += 1

			pixels[i, j] = (r, g, b)

	# Save the image with the hidden secret text
	image.save(output_path, format="PNG") # save as png to prevent jpeg loss compression
	print("Encoding finished")
				
# Extract secret data from image bit
def extract_bin(bit_data, remaining_len, current_string, img_bin):
	# stop extraction once all secret has been extracted
	if(remaining_len == 0): 
		return remaining_len, current_string

	bit_data[0] = bit_data[0] * 2 + (img_bin & 0x01)
	bit_data[1] += 1

	if(bit_data[1] == 8):
		char = chr(bit_data[0])

		if(char == '\t'):
			if(remaining_len == -1):
				remaining_len = int(current_string)
				current_string = ""
			else:
				return remaining_len, current_string
		else:
			current_string += char
			if remaining_len != -1:
				remaining_len -= 1

		bit_data[0] = 0
		bit_data[1] = 0
		
	return remaining_len, current_string

def decode(image, pixels):
	# Convert the binary text to ASCII
	current_string = ""
	remaining_len = -1
	bin_data = [0, 0] # bit_val, bit_len

	for i in range(image.width):
		if remaining_len == 0:
			print("Decoding finished")
			break

		for j in range(image.height):
			r, g, b = pixels[i, j]

			# Extract the least significant bit of each color channel
			remaining_len, current_string = extract_bin(bin_data, remaining_len, current_string, r)
			remaining_len, current_string = extract_bin(bin_data, remaining_len, current_string, g)
			remaining_len, current_string = extract_bin(bin_data, remaining_len, current_string, b)

	return current_string

def extract_text(image_path):
	# Open the image
	image = Image.open(image_path)

	# Extract the secret text from the image
	pixels = image.load()

	return decode(image, pixels)

if __name__ == '__main__':
	image_path = 'input/image.jpg'
	secret_text = 'this is a secret messsage'
	output_path = 'output/image.png'
	hide_text(image_path, secret_text, output_path)

	extracted_text = extract_text(output_path)
	print("Extracted text:", extracted_text)

