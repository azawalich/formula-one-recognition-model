FROM python:3.11.9-bookworm
WORKDIR /app/
ARG MINIO_URL
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG DEBUGGING_LOCAL
ADD requirements /tmp
# install packages
RUN apt update && apt upgrade -y \
&& apt install -y $(cat /tmp/apt) \
&& python -m pip install --no-cache-dir $(echo `cat /tmp/python`) \
# compile openh264
&& cd /tmp \
&& tar -xvzf ffmpeg-7.0.1.tar.gz -C /usr/local/src/ \
&& tar -xvzf openh264-2.4.1.tar.gz -C /usr/local/src/ \
&& cd /usr/local/src/openh264-2.4.1 \
&& make -j$(nproc) \
&& make -j$(nproc) install \
&& ln -s -f /usr/local/lib/libopenh264.so.0 /usr/lib/x86_64-linux-gnu/ \
# compile ffmpeg
&& cd /usr/local/src/ffmpeg-7.0.1 \
&& mkdir /usr/local/share/doc \
&& ./configure --enable-ffplay --enable-libxcb --enable-gpl --enable-version3 --enable-postproc --enable-libvorbis --enable-libvpx --enable-librtmp --enable-libx264 --enable-libtheora --enable-libvpx --enable-libwebp --enable-lsp --enable-libmp3lame --enable-libopus --enable-libspeex --enable-libopenh264 --enable-libfreetype \
&& make -j$(nproc) \
&& make -j$(nproc) install \
# compile opencv with above to python3
&& cd /tmp \
&& unzip opencv-4.x.zip \
&& unzip opencv_contrib-4.x.zip \
&& mkdir -p build && cd build \ 
&& cmake ../ -G "Ninja" -D BUILD_SHARED_LIBS=OFF -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.x/modules ../opencv-4.x -D BUILD_opencv_python2=OFF -D BUILD_opencv_python3=ON -D PYTHON_VERSION=311 -D PYTHON_DEFAULT_EXECUTABLE=/usr/local/bin/python3.11 -D PYTHON3_EXECUTABLE=/usr/local/bin/python3.11 -D PYTHON3_PACKAGES_PATH=/usr/local/lib/python3.11/site-packages -D PYTHON3_INCLUDE_DIR=/usr/local/include/python3.11 -D OPENCV_PYTHON3_INSTALL_PATH=/usr/local/lib/python3.11/site-packages -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/lib/python3.11/site-packages/numpy/core/include/ \
&& cmake --build . --parallel $(nproc) \
&& cmake --install . --config Debug \
# cleanup
&& rm -rf /tmp/* && apt clean && apt autoremove \
&& cd /app/
ADD constants.py /app
ADD functions.py /app
ADD main.py /app
COPY static /app/static
COPY templates /app/templates
COPY vision /app/vision
COPY models /app/models
ENTRYPOINT ["python", "-m", "main.py", "--minio-url", "$MINIO_URL", "--access-key", "$MINIO_ACCESS_KEY", "--secret-key", "$MINIO_SECRET_KEY", "--debugging-local", "$DEBUGGING_LOCAL"]